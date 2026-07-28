from __future__ import annotations

import os

from neo4j import AsyncDriver, AsyncGraphDatabase

_driver: AsyncDriver | None = None


def init_driver() -> None:
    global _driver
    if _driver is not None:
        return

    uri = os.getenv("NEO4J_URI")
    if not uri:
        return

    _driver = AsyncGraphDatabase.driver(
        uri,
        auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD")),
    )


def get_driver() -> AsyncDriver:
    if _driver is None:
        init_driver()

    if _driver is None:
        raise RuntimeError("NEO4J_URI가 설정되지 않아 Neo4j 드라이버를 초기화할 수 없습니다.")

    return _driver


async def dispose_driver() -> None:
    global _driver
    if _driver is not None:
        await _driver.close()
    _driver = None
