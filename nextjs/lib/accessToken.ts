/**
 * 액세스 토큰 획득 지점 — NEXT-004 §5.0
 *
 * 이 저장소에는 아직 토큰을 저장·갱신하는 코드가 없다.
 * `components/auth/AuthPanel.tsx`의 로그인 핸들러는 `onSuccess()`만 부르는 스텁이고,
 * `OAuthRedirectHandler`는 `?auth=success`를 보고 리다이렉트만 한다.
 * 토큰을 어디에 보관할지는 NEXT-004 §9 결정 2번이며 아직 정해지지 않았다.
 *
 * 그래서 획득 경로를 이 함수 하나로 격리해 둔다. 인증 플로우가 붙으면
 * **이 파일만** 고치면 되고 `lib/receiptApi.ts`는 건드리지 않는다.
 *
 * 지금은 항상 null을 반환하며, 그 상태에서도 /ledger 화면은
 * "로그인이 필요합니다" 안내로 정상 동작해야 한다.
 */
export function getAccessToken(): string | null {
  return null;
}
