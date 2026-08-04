# Flutter 카카오 OIDC 로그인 하네스 (모바일 클라이언트)

Flutter 앱(`flutter/`, 패키지명 `taper`)에서 **카카오 로그인 → `id_token` 획득 →
자체 인증 게이트웨이에 제출 → 자체 JWT 수령·보관·갱신**까지의 클라이언트 스펙이다.

- 기준일: 2026-08-03
- 대상: Flutter 3.44 stable(Dart 3.12) / `com.ragtailor.taper` / Android 실기기
- 짝 문서(서버): [`fastapi/_docs/fast-003-flutter-kakao-oauth-harness.md`](../../fastapi/_docs/fast-003-flutter-kakao-oauth-harness.md)
- 기기 연결·빌드 절차: [`flutter-android-harness.md`](flutter-android-harness.md)
- **이 문서는 스펙이며 구현 코드를 포함하지 않는다.** 각 단계의 "검증"으로 완료를 판정한다.

> **역할 분담 한 줄 요약**: 앱은 카카오에서 `id_token`을 받아 **그대로 서버에 넘기는 일만** 한다.
> 사용자 정보 판단, 회원가입 여부, 세션 수명은 전부 서버가 정한다.
> 앱이 `id_token`을 직접 디코드해 화면에 쓰는 코드는 만들지 않는다.

---

## 1. 현재 저장소 상태 (전제 확인)

착수 전에 이 표가 여전히 맞는지 확인한다. 문서와 저장소가 어긋나면 **저장소가 기준**이다.

| 항목 | 현재 값 | 이번 작업에서 |
|------|---------|---------------|
| 패키지명 | `taper` (`pubspec.yaml`) | 그대로 |
| applicationId / namespace | `com.ragtailor.taper` | **카카오 콘솔에 등록할 값** |
| Dart SDK 제약 | `^3.10.8` | 그대로 |
| 의존성 | `cupertino_icons`, `video_player`만 | 카카오 SDK·보안 저장소·HTTP 추가 |
| `lib/` | `main.dart`, `stopwatch_page.dart` | 로그인 화면·인증 계층 추가 |
| 생성된 플랫폼 | `android/`, `web/`, `windows/` | — |
| **`ios/` 디렉터리** | **없음** | §4.2 참고 — iOS는 플랫폼 생성부터 |
| `flutter/CLAUDE.md` | 비어 있음 | 이번 작업 중 채우면 좋다(선택) |

`ios/`가 없으므로 **이번 작업의 실기기 검증 대상은 안드로이드다.** iOS 설정은 §4.2에 스펙만 적어 두고,
`flutter create --platforms=ios .` 로 플랫폼을 생성한 뒤 적용한다.

---

## 2. 카카오 개발자 콘솔 준비

앱 코드를 건드리기 전에 콘솔이 먼저 맞아야 한다. 여기서 틀리면 증상이 전부
"KOE006 / KOE101 / invalid_client" 같은 모호한 에러로만 나온다.

| 항목 | 값 / 확인 위치 | 왜 필요한가 |
|------|----------------|-------------|
| 앱 키 — 네이티브 앱 키 | 내 애플리케이션 → 앱 키 | Android/iOS SDK 초기화 |
| 앱 키 — JavaScript 키 | 동일 | 웹 빌드에서 SDK 초기화 |
| 앱 키 — **REST API 키** | 동일 | **`id_token`의 `aud`가 이 값이다.** 서버 `KAKAO_CLIENT_ID`와 일치해야 함 |
| **OpenID Connect 활성화** | 제품 설정 → 카카오 로그인 → OpenID Connect | **끄면 `id_token`이 아예 안 온다.** 이번 작업의 필수 스위치 |
| 카카오 로그인 활성화 | 제품 설정 → 카카오 로그인 | |
| 플랫폼 등록 (Android) | 앱 설정 → 플랫폼 → Android | 패키지명 `com.ragtailor.taper` + **키 해시** |
| 키 해시 | 디버그·릴리스 **각각** 등록 | 하나만 넣으면 릴리스 빌드에서만 실패한다 |
| 동의 항목 | 카카오 로그인 → 동의항목 | `profile_nickname`, `account_email`(선택 동의 가능) |
| Redirect URI | 카카오 로그인 → Redirect URI | **웹 인가코드 플로우용.** 모바일 SDK 로그인에는 불필요 |

- 키 해시는 서명 키의 SHA-1을 base64로 인코딩한 값이다. 디버그 키(`~/.android/debug.keystore`,
  기본 비밀번호 `android`)와 릴리스 키에서 각각 뽑는다. **WSL과 Windows의 debug.keystore가
  다르면 키 해시도 다르다** — 실제로 빌드하는 쪽 것을 등록한다.
- 서버 `.env`의 `KAKAO_CLIENT_ID`는 kingsman(웹 인가코드 플로우)이 이미 쓰고 있다.
  **모바일용 카카오 앱을 새로 팠다면 서버가 허용 `aud` 목록을 가져야 한다** — 서버 문서 §9-1.

**검증:** 콘솔에서 OpenID Connect가 "ON", Android 플랫폼에 패키지명과 키 해시 2개가 보인다.

---

## 3. 의존성과 앱 키 주입

`pubspec.yaml`에 추가한 것(2026-08-03 기준 실제 해석된 버전):

| 패키지 | 버전 | 용도 |
|--------|------|------|
| `kakao_flutter_sdk_user` | `^2.0.0` | 카카오 로그인. `KakaoSdk`·`OAuthToken`·예외 타입까지 re-export 하므로 이 하나면 된다 |
| `flutter_secure_storage` | `^10.3.1` | 리프레시 토큰 보관 (Android Keystore / iOS Keychain). minSdk 23 이상 필요 |
| `http` | `^1.2.0` | 게이트웨이 호출 |

**앱 키는 소스에 하드코딩하지 않는다.** `--dart-define`(또는 `--dart-define-from-file`)로 주입한다.

| 컴파일 상수 | 값 | 비고 |
|-------------|-----|------|
| `KAKAO_NATIVE_APP_KEY` | 네이티브 앱 키 | Android/iOS |
| `KAKAO_JS_APP_KEY` | JavaScript 키 | 웹 빌드에서만 |
| `AUTH_BASE_URL` | `https://auth.ragtailor.com` | 로컬은 개발 서버 주소 |

> 주의: `--dart-define` 값은 **비밀이 아니다.** 빌드 산출물에서 추출 가능하다.
> 카카오 앱 키는 원래 클라이언트에 배포되는 공개값이므로 문제없지만, 이 방식으로
> **서버 시크릿을 넘기지 않는다.** 앱에 들어가도 되는 값은 앱 키와 base URL뿐이다.

**검증:** `flutter pub get` 성공, `flutter analyze` 무경고.

---

## 4. 플랫폼 설정

### 4.1 Android

`android/app/src/main/AndroidManifest.xml`에 아래를 **추가**한다.
기존 `MainActivity`, 네이티브 `StopwatchActivity`, `<queries>` 블록은 손대지 않는다
(`<queries>`는 이미 존재하므로 **새로 만들지 말고 항목만 추가**한다).

| 위치 | 추가할 것 | 값 |
|------|-----------|-----|
| `<application>` 안 | 카카오 리다이렉트 액티비티에 붙일 intent-filter | 액티비티 이름 `com.kakao.sdk.flutter.auth.AuthCodeHandlerActivity`, `exported=true` |
| 위 액티비티의 intent-filter | `VIEW` / `DEFAULT` / `BROWSABLE` + data | scheme `kakao{NATIVE_APP_KEY}`, host `oauth` |
| `<manifest>` | 인터넷 권한 | `android.permission.INTERNET` |

- 액티비티 **본체는 SDK(`kakao_flutter_sdk_auth`)의 매니페스트가 이미 선언한다.**
  앱 매니페스트에는 같은 이름으로 intent-filter만 얹으면 매니페스트 병합이 합쳐 준다.
- 카카오톡 패키지 가시성(`<queries>`)도 **`kakao_flutter_sdk_common`이 자체 매니페스트에서
  선언한다.** 앱 매니페스트에 따로 추가할 필요가 없다(v2.0.0 기준, 병합 결과로 확인).
- scheme의 `{NATIVE_APP_KEY}`는 매니페스트에 문자열로 박힌다. `--dart-define`은 Dart 상수라
  매니페스트가 읽지 못하므로, gradle `manifestPlaceholders`로 주입한다
  (이 저장소는 `android/local.properties`의 `kakao.nativeAppKey`를 읽는다).

**검증:** `flutter build apk --debug` 성공 후 실기기 설치 → 카카오톡이 뜬다.
`adb logcat`에 `KakaoSdk` 초기화 로그가 보이고 `KOE` 에러가 없다.

### 4.2 iOS (플랫폼 생성 후)

`ios/`가 아직 없다. 생성 후 `Info.plist`에 아래를 넣는다.

| 키 | 값 |
|----|-----|
| `LSApplicationQueriesSchemes` | `kakaokompassauth`, `kakaolink`, `kakaoplus` |
| `CFBundleURLTypes` → `CFBundleURLSchemes` | `kakao{NATIVE_APP_KEY}` |

번들 ID를 카카오 콘솔의 iOS 플랫폼에 등록해야 한다. 안드로이드 패키지명과 별개 항목이다.

### 4.3 Web

웹은 **JavaScript 키**로 초기화하고, 카카오 콘솔에 웹 플랫폼 도메인과 Redirect URI를 등록해야 한다.
서버에는 `platform: "web"`으로 보낸다. 웹은 쿠키 기반 세션을 쓰므로 모바일과 저장 전략이 다르다
(서버 문서 §3.2) — **웹 로그인은 이 문서의 범위 밖이다.** 앱 코드에서 웹/모바일 분기만 남긴다.

---

## 5. 로그인 흐름

```text
[앱] nonce 생성 (암호학적 난수, 1회용)
  │
  ├─ 카카오톡 설치됨 → loginWithKakaoTalk(nonce)
  └─ 미설치/실패     → loginWithKakaoAccount(nonce)   (웹뷰/커스텀탭 계정 로그인)
  │
  ▼ OAuthToken.idToken 수령           ← OIDC 미활성화면 여기가 null 이다
[앱] POST {AUTH_BASE_URL}/auth/kakao/login
        { "id_token": "...", "platform": "mobile", "nonce": "<위와 같은 값>" }
  │
  ▼ 자체 access / refresh 수령
[앱] access = 메모리, refresh = flutter_secure_storage
```

- **`nonce`는 앱이 만들고, 카카오 로그인에 넣은 값과 서버에 보내는 값이 같아야 한다.**
  서버가 `id_token.nonce`와 대조해 재생 공격을 막는다. 매 로그인마다 새로 만든다.
- `loginWithKakaoTalk`은 카카오톡이 설치돼 있어도 실패할 수 있다(사용자 취소, 구버전 등).
  **실패 시 `loginWithKakaoAccount`로 폴백**한다. 단, 사용자가 명시적으로 취소한 경우
  (취소 에러 코드)에는 폴백하지 말고 조용히 로그인 화면으로 돌아간다 — 안 그러면
  취소했는데 웹 로그인이 다시 뜬다.
- 카카오가 준 `kakao_account.email` / `nickname`을 **서버로 보내지 않는다.** 서버는 무시한다.
  화면에 이름을 표시해야 하면 서버 응답이나 별도 프로필 API에서 받는다.

---

## 6. 서버 계약

베이스 URL: `https://auth.ragtailor.com` (`--dart-define AUTH_BASE_URL`)

### 6.1 로그인

```text
POST /auth/kakao/login
{ "id_token": "<카카오 id_token>", "platform": "mobile", "nonce": "<1회용 난수>" }

200 { "access_token": "...", "refresh_token": "...", "token_type": "bearer",
      "expires_in": 3600, "platform": "mobile" }
```

### 6.2 갱신 / 로그아웃

```text
POST /auth/refresh   { "refresh_token": "...", "platform": "mobile" }
POST /auth/logout    { "refresh_token": "...", "platform": "mobile" }
```

- `platform`은 **모든 요청에 필수**다. 빠지면 400이다.
- **모바일은 쿠키를 쓰지 않는다.** 서버는 `platform="mobile"`이면 `Set-Cookie`를 붙이지 않는다.
  토큰은 응답 body에서만 읽는다.
- 모바일 세션과 웹 세션은 서버에서 분리돼 있다. 앱에서 로그아웃해도 **같은 계정의 웹 세션은 살아 있다.**
  UI 문구를 "모든 기기에서 로그아웃"으로 쓰지 않는다.

### 6.3 에러 처리

| 상태 | 원인 | 앱 동작 |
|------|------|---------|
| 400 | `platform` 누락/오타 | 버그다. 릴리스 전에 잡는다 |
| 401 (로그인) | `id_token` 서명·`aud`·만료·`nonce` 불일치 | 카카오 로그인부터 다시. 저장된 토큰 폐기 |
| 401 (refresh) | 만료·재사용 감지·플랫폼 불일치 | **저장된 refresh 삭제 후 로그인 화면**. 재시도 루프 금지 |
| 503 | 서버가 카카오 JWKS를 못 얻음 | 앱 잘못이 아니다. "잠시 후 다시" 안내 + 재시도 버튼 |
| 네트워크 오류 | | 지수 백오프 재시도. 토큰은 지우지 않는다 |

401과 네트워크 오류를 같이 처리하지 않는다. **네트워크가 끊겼다고 로그아웃시키면 안 된다.**

---

## 7. 토큰 보관과 갱신

| 토큰 | 저장 위치 | 이유 |
|------|-----------|------|
| access | **메모리만** | 수명이 짧다. 디스크에 쓸 이유가 없다 |
| refresh | `flutter_secure_storage` | Android Keystore / iOS Keychain |
| 카카오 토큰 | 카카오 SDK가 알아서 보관 | 앱이 따로 저장하지 않는다 |

- `SharedPreferences`에 토큰을 넣지 않는다(평문이다).
- 앱 시작 시: secure storage에 refresh가 있으면 `/auth/refresh` 1회 → 성공하면 로그인 상태 복원,
  401이면 삭제하고 로그인 화면.
- 401 응답 시 **refresh 1회만** 시도하고, 그 결과로 원 요청을 1회 재시도한다. 2회 이상 반복 금지.
- **갱신 동시성**: 화면 여러 개가 동시에 401을 받으면 refresh 요청이 여러 번 나간다.
  서버는 로테이션 방식이라 **두 번째 요청이 "재사용"으로 판정돼 세션이 통째로 날아간다.**
  refresh 호출은 반드시 **단일 in-flight로 묶고**, 나머지는 그 결과를 기다린다. 이 항목이
  이번 작업에서 가장 깨지기 쉬운 부분이다.
- 로그마다 토큰을 찍지 않는다. `id_token`·refresh는 **어떤 로그에도 남기지 않는다**(§11).

---

## 8. 로그아웃 / 연결 끊기

| 동작 | 해야 할 일 |
|------|-----------|
| 로그아웃 | ① 서버 `POST /auth/logout {platform:"mobile"}` → ② 카카오 SDK 로그아웃(로컬 토큰 폐기) → ③ secure storage 비우기 → ④ 메모리 access 폐기 |
| 연결 끊기(탈퇴) | 카카오 `unlink` + 서버 탈퇴 API — **이번 범위 밖** |

서버 호출이 실패해도 **로컬 정리(②③④)는 반드시 수행**한다. 서버 슬롯은 TTL로 만료된다.

---

## 9. 작업 순서

각 단계마다 검증을 통과시키고 다음으로 간다.

| # | 단계 | 검증 |
|---|------|------|
| 1 | 카카오 콘솔 설정 (§2) | OIDC ON, Android 플랫폼에 패키지명 + 키 해시 2개 |
| 2 | 의존성 추가 + 앱 키 주입 (§3) | `flutter pub get`, `flutter analyze` 클린 |
| 3 | Android 매니페스트 (§4.1) | `flutter build apk --debug` 성공, 실기기 설치 |
| 4 | SDK 초기화 + 로그인 화면 | 버튼 → 카카오톡/계정 로그인 화면이 뜬다 |
| 5 | `id_token` 획득 (§5) | `idToken != null` (null이면 §2의 OIDC 스위치를 다시 본다) |
| 6 | 게이트웨이 연동 (§6) | 200 응답 + access/refresh 수령. 서버 로그에 KAPI 호출 없음 |
| 7 | 토큰 보관·자동 갱신 (§7) | 앱 재시작 후 로그인 유지, access 만료 후 자동 갱신 |
| 8 | 로그아웃 (§8) | 재시작 시 로그인 화면 |
| 9 | 회귀 (§10) | 표 전체 통과 |

**검증 명령**

```bash
cd flutter
flutter pub get
flutter analyze
flutter test
flutter run --dart-define=KAKAO_NATIVE_APP_KEY=... --dart-define=AUTH_BASE_URL=...
adb logcat | grep -iE "kakao|auth"
```

서버가 로컬이면 실기기에서 `localhost`는 **기기 자신**을 가리킨다. 개발 PC의 LAN IP를 쓰거나
`adb reverse tcp:9000 tcp:9000`으로 포워딩한다.

---

## 10. 회귀 시나리오

| # | 시나리오 | 기대 |
|---|----------|------|
| 1 | 카카오톡 설치 기기에서 로그인 | 카카오톡으로 전환 → 앱 복귀 → 로그인 성공 |
| 2 | 카카오톡 미설치(또는 로그아웃) 기기 | 계정 로그인 화면으로 폴백 → 성공 |
| 3 | 카카오 로그인 도중 사용자가 취소 | 앱이 로그인 화면 유지. 웹 로그인이 **다시 뜨지 않는다** |
| 4 | 앱 강제 종료 후 재시작 | refresh로 세션 복원, 재로그인 요구 없음 |
| 5 | access 만료 상태에서 API 호출 | 자동 갱신 후 원 요청 성공. 사용자에게 아무 일도 안 보임 |
| 6 | 동시에 여러 요청이 401 | refresh 요청은 **1회만** 나간다(§7 동시성) |
| 7 | 앱에서 로그아웃 | 앱은 로그인 화면. **같은 계정 웹 세션은 살아 있다** |
| 8 | 비행기 모드에서 API 호출 | 재시도 안내. **로그아웃되지 않는다** |
| 9 | 릴리스 서명으로 빌드 | 로그인 성공(릴리스 키 해시 등록 확인) |

---

## 11. 보안 체크리스트

- [ ] `id_token`·access·refresh를 `print`/`debugPrint`/로그 파일에 출력하지 않는다.
- [ ] refresh는 secure storage에만. `SharedPreferences`·평문 파일 금지.
- [ ] 앱 키·URL은 `--dart-define` 주입. 소스에 하드코딩하지 않는다.
- [ ] **서버 시크릿(JWT 개인키 등)은 앱에 어떤 형태로도 넣지 않는다.**
- [ ] 앱이 `id_token`을 디코드해 사용자 신원을 판단하지 않는다. 판단은 서버가 한다.
- [ ] HTTPS만 사용. 개발 편의로 인증서 검증을 끄는 코드를 커밋하지 않는다.
- [ ] 401 처리에 무한 재시도 루프가 없다.

---

## 12. 범위 밖 / 결정 필요

**범위 밖**

- 웹(Flutter Web / Next.js) 로그인 UI와 쿠키·CSRF 정책.
- iOS 실기기 검증 — `ios/` 플랫폼 생성 후 별도 작업.
- 카카오 상세 프로필 조회(KAPI), 카카오톡 메시지·친구 API.
- 애플/구글 로그인.
- 회원 탈퇴(unlink), 프로필 수정.
- 다중 기기 동시 로그인 — 서버가 플랫폼당 세션 1개만 유지한다(서버 문서 §3.3).
  **폰과 태블릿에 동시에 로그인하면 먼저 기기가 밀려난다.**

**결정 필요**

1. 모바일용 카카오 앱을 새로 팔 것인가, 웹과 같은 앱을 쓸 것인가 → 서버 `aud` 설정이 달라진다.
2. HTTP 클라이언트를 `http`로 갈지 `dio`로 갈지(인터셉터가 필요하면 `dio`).
3. 로그인 화면을 기존 인트로 영상 → 스톱워치 흐름의 어디에 끼울 것인가.
4. `email` 동의를 필수로 받을 것인가 — 선택 동의면 서버가 `email` 없는 유저를 허용해야 한다.
