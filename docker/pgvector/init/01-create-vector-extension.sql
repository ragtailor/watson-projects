-- pgvector 익스텐션 생성 (컨테이너 최초 초기화 시 1회만 실행된다)
-- 볼륨(pgvector_data)이 이미 초기화된 상태라면 이 스크립트는 실행되지 않으므로,
-- 그때는 수동으로: docker compose exec pgvector psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c 'CREATE EXTENSION IF NOT EXISTS vector;'
CREATE EXTENSION IF NOT EXISTS vector;
