#!/usr/bin/env bash
set -euo pipefail

# RS256 키쌍 생성.
#  - jwt_private.pem : auth 컨테이너 전용 (절대 백엔드로 넘기지 않는다)
#  - jwt_public.pem  : 모든 컨테이너의 검증 경로에서 사용
#
# PEM은 여러 줄이라 환경변수 주입이 까다롭다. base64 한 줄로 인코딩해 주입하면
# core/config.py 의 _decode_key_material 이 자동으로 디코드한다.
#   base64 -w0 jwt_private.pem   → .env.auth 의 JWT_PRIVATE_KEY
#   base64 -w0 jwt_public.pem    → .env.backend 의 JWT_PUBLIC_KEY

openssl genrsa -out jwt_private.pem 2048
openssl rsa -in jwt_private.pem -pubout -out jwt_public.pem

echo "jwt_private.pem → .env.auth 의 JWT_PRIVATE_KEY 로"
echo "jwt_public.pem  → .env.backend 의 JWT_PUBLIC_KEY 로"
echo "(멀티라인 주입이 어려우면: base64 -w0 <파일> 결과를 값으로 사용)"
