"""리프레시 세션 저장소 — 유저 1인당 Redis Hash + 플랫폼별 필드.

    auth:session:{sub}   (Hash)
      ├─ web    : {"th": "<sha256>", "jti": "...", "iat": ..., "exp": ...}
      └─ mobile : {"th": "<sha256>", "jti": "...", "iat": ..., "exp": ...}

- 리프레시 토큰 원문을 저장하지 않는다. SHA-256 해시와 메타만 남긴다.
- 플랫폼별로 슬롯이 완전히 분리된다. mobile 로그아웃이 web 세션을 건드리지 않는다.
- 필드 단위 TTL이 없으므로 만료 판정은 값 안의 exp로 여기서 한다.
  Hash 자체의 EXPIRE는 고아 키 청소용 보조 장치다(가장 긴 슬롯 기준).

접두어가 `auth:session:`인 이유: 기존 `auth:refresh:{jti}`(String)와 같은 네임스페이스에
Hash를 섞으면 운영 중 타입을 구분할 수 없고 잘못된 명령이 WRONGTYPE으로 죽는다.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass

_SESSION_KEY = "auth:session:{sub}"


@dataclass(frozen=True)
class RefreshSlot:
    """플랫폼 슬롯 하나에 저장된 리프레시 메타."""

    th: str
    jti: str
    iat: int
    exp: int


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _redis():
    """totem Redis 클라이언트를 지연 조회한다(모듈 import를 가볍게 유지)."""
    from core.matrix.totem_redis_cache_manager import get_client

    return get_client()


async def save(sub: str, platform: str, token: str, jti: str, ttl_sec: int) -> None:
    """해당 플랫폼 슬롯을 새 리프레시로 덮어쓴다(로테이션 포함)."""
    now = int(time.time())
    slot = RefreshSlot(th=token_hash(token), jti=jti, iat=now, exp=now + ttl_sec)

    client = _redis()
    key = _SESSION_KEY.format(sub=sub)
    await client.hset(key, platform, json.dumps(slot.__dict__))

    # 다른 플랫폼 슬롯의 수명을 깎지 않도록, 더 긴 쪽으로만 늘린다.
    current_ttl = await client.ttl(key)
    if current_ttl is None or current_ttl < ttl_sec:
        await client.expire(key, ttl_sec)


async def get(sub: str, platform: str) -> RefreshSlot | None:
    """살아 있는 슬롯을 반환한다. 없거나 만료됐으면 None."""
    client = _redis()
    raw = await client.hget(_SESSION_KEY.format(sub=sub), platform)
    if not raw:
        return None

    try:
        slot = RefreshSlot(**json.loads(raw))
    except (TypeError, ValueError):
        # 형식이 깨진 값은 없는 것으로 본다.
        return None

    if slot.exp <= int(time.time()):
        await revoke(sub, platform)
        return None
    return slot


async def matches(sub: str, platform: str, token: str) -> bool:
    """이 토큰이 해당 플랫폼의 현재 활성 리프레시인지."""
    slot = await get(sub, platform)
    return slot is not None and slot.th == token_hash(token)


async def revoke(sub: str, platform: str) -> None:
    """해당 플랫폼 슬롯만 지운다. 다른 플랫폼 세션은 그대로 둔다."""
    client = _redis()
    await client.hdel(_SESSION_KEY.format(sub=sub), platform)
