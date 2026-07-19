# 1. 파이썬 기본 이미지 선택
FROM python:3.13-slim

# 2. 컨테이너 내부 작업 디렉토리 설정
WORKDIR /tailor

# 3. 종속성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3-1. 런타임 보강 (별도 레이어: 위 torch 포함 대용량 설치 캐시를 보존하기 위함)
#  - opencv(ultralytics)가 요구하는 시스템 라이브러리
#  - requirements.txt 누락분 seaborn (추후 requirements 통합 예정)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxcb1 libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir seaborn==0.13.2

# 4. 나머지 소스 코드 복사
COPY . .

# 5. FastAPI 실행 명령어 (8000 포트 오픈)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
