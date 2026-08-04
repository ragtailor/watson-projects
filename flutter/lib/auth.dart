import 'dart:async';
import 'dart:convert';
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:kakao_flutter_sdk_user/kakao_flutter_sdk_user.dart';

import 'stopwatch_page.dart';

/// 빌드 시 주입하는 설정. 앱 키와 서버 주소를 소스에 박지 않는다.
///
/// ```bash
/// flutter run \
///   --dart-define=KAKAO_NATIVE_APP_KEY=<네이티브 앱 키> \
///   --dart-define=AUTH_BASE_URL=https://auth.ragtailor.com
/// ```
///
/// 안드로이드 리다이렉트 스킴(`kakao<네이티브 앱 키>://oauth`)은 매니페스트가 읽어야 해서
/// `--dart-define`으로 전달할 수 없다. `android/local.properties`의 `kakao.nativeAppKey`에
/// **같은 값**을 넣어 둔다.
class AuthConfig {
  const AuthConfig._();

  static const String kakaoNativeAppKey =
      String.fromEnvironment('KAKAO_NATIVE_APP_KEY');

  static const String authBaseUrl = String.fromEnvironment(
    'AUTH_BASE_URL',
    defaultValue: 'https://auth.ragtailor.com',
  );

  /// 서버는 세션을 web / mobile로 나눠 보관한다. 이 앱은 언제나 mobile이다.
  static const String platform = 'mobile';

  static bool get isConfigured => kakaoNativeAppKey.isNotEmpty;
}

/// 사용자가 카카오 로그인 화면에서 직접 취소했다. 에러가 아니므로 조용히 되돌아간다.
class AuthCancelled implements Exception {
  const AuthCancelled();
}

/// 사용자에게 보여줄 수 있는 로그인 실패.
class AuthFailure implements Exception {
  const AuthFailure(this.message);

  final String message;

  @override
  String toString() => message;
}

/// 모바일 세션 하나를 관리한다.
///
/// - access token은 **메모리에만** 둔다. 수명이 짧아 디스크에 남길 이유가 없다.
/// - refresh token만 보안 저장소(Android Keystore / iOS Keychain)에 남긴다.
///   앱을 다시 켜면 [restore]가 이 값으로 세션을 되살린다.
/// - 서버는 이 세션을 유저별 Redis 해시의 `mobile` 필드에 기록한다. 웹 세션과 슬롯이
///   분리돼 있어 앱에서 로그아웃해도 같은 계정의 웹 세션은 살아 있다.
class AuthSession {
  AuthSession._();

  static final AuthSession instance = AuthSession._();

  static const String _refreshTokenKey = 'auth.mobile.refresh_token';
  static const Duration _timeout = Duration(seconds: 10);

  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  String? _accessToken;
  DateTime? _accessExpiresAt;

  /// 갱신 요청은 한 번에 하나만 내보낸다.
  ///
  /// 서버가 리프레시 로테이션 방식이라 같은 토큰으로 두 번 요청하면 뒤의 것이 "재사용"으로
  /// 판정돼 세션이 통째로 폐기된다. 동시에 들어온 호출은 진행 중인 요청 결과를 함께 쓴다.
  Future<bool>? _refreshing;

  String? get accessToken => _accessToken;

  bool get isSignedIn =>
      _accessToken != null &&
      (_accessExpiresAt?.isAfter(DateTime.now()) ?? false);

  /// 저장된 리프레시 토큰으로 세션을 복원한다. 성공하면 true.
  ///
  /// 네트워크 오류일 때는 토큰을 지우지 않는다 — 비행기 모드로 들어갔다고 로그아웃시키면
  /// 안 된다. 서버가 401(만료·폐기·플랫폼 불일치)을 준 경우에만 지운다.
  Future<bool> restore() {
    final Future<bool>? pending = _refreshing;
    if (pending != null) {
      return pending;
    }
    final Future<bool> started = _refresh();
    _refreshing = started;
    return started.whenComplete(() {
      if (identical(_refreshing, started)) {
        _refreshing = null;
      }
    });
  }

  Future<bool> _refresh() async {
    final String? refreshToken = await _storage.read(key: _refreshTokenKey);
    if (refreshToken == null) {
      return false;
    }

    final http.Response response;
    try {
      response = await _post('/auth/refresh', <String, String>{
        'refresh_token': refreshToken,
        'platform': AuthConfig.platform,
      });
    } on Object {
      return false;
    }

    if (response.statusCode == 200) {
      await _save(response.body);
      return true;
    }
    if (response.statusCode == 401) {
      await signOutLocally();
    }
    return false;
  }

  /// 카카오 로그인 → `id_token`을 인증 게이트웨이에 제출 → 자체 토큰 수령.
  ///
  /// 사용자가 취소하면 [AuthCancelled], 그 밖의 실패는 [AuthFailure]를 던진다.
  Future<void> signInWithKakao() async {
    if (!AuthConfig.isConfigured) {
      throw const AuthFailure(
        'KAKAO_NATIVE_APP_KEY가 비어 있습니다. --dart-define으로 앱 키를 주입해 주세요.',
      );
    }

    // 재생 공격 방지값. 카카오에 넘긴 값과 서버로 보내는 값이 같아야 하며,
    // 서버가 id_token의 nonce 클레임과 대조한다.
    final String nonce = _newNonce();
    final OAuthToken token = await _kakaoLogin(nonce);

    final String? idToken = token.idToken;
    if (idToken == null) {
      throw const AuthFailure(
        'ID 토큰을 받지 못했습니다. 카카오 개발자 콘솔에서 OpenID Connect를 활성화해 주세요.',
      );
    }

    final http.Response response;
    try {
      response = await _post('/auth/kakao/login', <String, String>{
        'id_token': idToken,
        'platform': AuthConfig.platform,
        'nonce': nonce,
      });
    } on Object {
      throw const AuthFailure('인증 서버에 연결하지 못했습니다. 네트워크를 확인해 주세요.');
    }

    if (response.statusCode != 200) {
      throw AuthFailure(_messageFor(response));
    }
    await _save(response.body);
  }

  /// 카카오톡이 있으면 카카오톡으로, 없거나 실패하면 카카오계정으로 로그인한다.
  Future<OAuthToken> _kakaoLogin(String nonce) async {
    if (await isKakaoTalkInstalled()) {
      try {
        return await UserApi.instance.loginWithKakaoTalk(nonce: nonce);
      } on Object catch (error) {
        // 사용자가 직접 취소했다면(뒤로 가기 등) 카카오계정 로그인으로 넘어가지 않는다.
        // 넘어가면 취소했는데 로그인 화면이 다시 뜬다.
        if (_isCancelled(error)) {
          throw const AuthCancelled();
        }
        // 카카오톡에 연결된 계정이 없는 경우 등 — 카카오계정 로그인으로 이어간다.
      }
    }

    try {
      return await UserApi.instance.loginWithKakaoAccount(nonce: nonce);
    } on Object catch (error) {
      if (_isCancelled(error)) {
        throw const AuthCancelled();
      }
      throw AuthFailure('카카오 로그인에 실패했습니다. ($error)');
    }
  }

  static bool _isCancelled(Object error) {
    if (error is KakaoClientException) {
      return error.reason == ClientErrorCause.cancelled;
    }
    if (error is PlatformException) {
      return error.code == 'CANCELED';
    }
    return false;
  }

  /// 서버 세션(mobile 슬롯), 카카오 로컬 토큰, 기기에 저장된 토큰을 모두 정리한다.
  ///
  /// 서버 호출이 실패해도 로컬 정리는 반드시 수행한다. 남은 서버 슬롯은 TTL로 만료된다.
  Future<void> signOut() async {
    final String? refreshToken = await _storage.read(key: _refreshTokenKey);
    if (refreshToken != null) {
      try {
        await _post('/auth/logout', <String, String>{
          'refresh_token': refreshToken,
          'platform': AuthConfig.platform,
        });
      } on Object {
        // 서버에 못 닿아도 로컬은 지운다.
      }
    }
    try {
      await UserApi.instance.logout();
    } on Object {
      // 카카오 토큰이 이미 없을 수 있다.
    }
    await signOutLocally();
  }

  /// 서버를 부르지 않고 이 기기에 남은 세션만 지운다.
  Future<void> signOutLocally() async {
    _accessToken = null;
    _accessExpiresAt = null;
    await _storage.delete(key: _refreshTokenKey);
  }

  Future<void> _save(String body) async {
    final Map<String, dynamic> json = jsonDecode(body) as Map<String, dynamic>;
    _accessToken = json['access_token'] as String?;
    final int? expiresIn = (json['expires_in'] as num?)?.toInt();
    _accessExpiresAt = expiresIn == null
        ? null
        : DateTime.now().add(Duration(seconds: expiresIn));

    final String? refreshToken = json['refresh_token'] as String?;
    if (refreshToken != null) {
      await _storage.write(key: _refreshTokenKey, value: refreshToken);
    }
  }

  Future<http.Response> _post(String path, Map<String, String> body) {
    return http
        .post(
          Uri.parse('${AuthConfig.authBaseUrl}$path'),
          headers: const <String, String>{'Content-Type': 'application/json'},
          body: jsonEncode(body),
        )
        .timeout(_timeout);
  }

  static String _messageFor(http.Response response) {
    switch (response.statusCode) {
      case 400:
        return '요청 형식이 올바르지 않습니다. (400)';
      case 401:
        return '카카오 인증 정보가 유효하지 않습니다. 다시 로그인해 주세요.';
      case 404:
        return '인증 서버에 로그인 엔드포인트가 없습니다. (404)';
      case 503:
        return '인증 서버가 카카오 공개키를 확인하지 못했습니다. 잠시 후 다시 시도해 주세요.';
      default:
        return '로그인에 실패했습니다. (${response.statusCode})';
    }
  }

  static String _newNonce() {
    final Random random = Random.secure();
    final List<int> bytes = List<int>.generate(32, (_) => random.nextInt(256));
    return base64UrlEncode(bytes).replaceAll('=', '');
  }
}

/// 카카오 로그인 화면.
///
/// 인트로 영상이 끝났을 때 살아 있는 모바일 세션이 없으면 이 화면이 뜬다.
/// 로그인에 성공하면 곧바로 스톱워치로 넘어간다.
class AuthPage extends StatefulWidget {
  const AuthPage({super.key});

  @override
  State<AuthPage> createState() => _AuthPageState();
}

class _AuthPageState extends State<AuthPage> {
  static const Color _kakaoYellow = Color(0xFFFEE500);
  static const Color _kakaoLabel = Color(0xD9000000);

  bool _busy = false;
  String? _error;

  Future<void> _signIn() async {
    if (_busy) {
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });

    final NavigatorState navigator = Navigator.of(context);
    try {
      await AuthSession.instance.signInWithKakao();
      if (!mounted) {
        return;
      }
      navigator.pushReplacement(
        MaterialPageRoute<void>(builder: (_) => const StopwatchPage()),
      );
    } on AuthCancelled {
      if (mounted) {
        setState(() => _busy = false);
      }
    } on AuthFailure catch (failure) {
      if (mounted) {
        setState(() {
          _busy = false;
          _error = failure.message;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              const Text(
                'AX Academy',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                  letterSpacing: -0.5,
                ),
              ),
              const SizedBox(height: 12),
              const Text(
                '카카오 계정으로 로그인하면\n다음부터 바로 시작합니다.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 14,
                  height: 1.6,
                  color: Color(0xFF9CA3AF),
                ),
              ),
              const SizedBox(height: 48),
              SizedBox(
                width: double.infinity,
                height: 52,
                child: Material(
                  color: _kakaoYellow,
                  borderRadius: BorderRadius.circular(6),
                  clipBehavior: Clip.antiAlias,
                  child: InkWell(
                    onTap: _busy ? null : _signIn,
                    child: Center(
                      child: _busy
                          ? const SizedBox(
                              width: 22,
                              height: 22,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: _kakaoLabel,
                              ),
                            )
                          : const Text(
                              '카카오로 로그인',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                                color: _kakaoLabel,
                              ),
                            ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              // 실패 사유를 화면에 그대로 보여준다. 설정 실수(앱 키 누락, OIDC 미활성화)가
              // 대부분이라 로그를 뒤지지 않고 바로 알 수 있어야 한다.
              SizedBox(
                height: 60,
                child: _error == null
                    ? null
                    : Text(
                        _error!,
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                          fontSize: 13,
                          height: 1.5,
                          color: Color(0xFFFF453A),
                        ),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
