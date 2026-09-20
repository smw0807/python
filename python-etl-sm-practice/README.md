# 문래역 통합고객 운영 Python ETL 실습 패키지

이 패키지는 `CSV/JSON 취합 → pandas 정제·가공 → PostgreSQL 적재 → FastAPI 조회 → Vue 화면` 흐름을 한 번에 연습하도록 구성했습니다. Node.js/TypeScript/Vue 경험자가 Python 데이터 처리 방식과 운영 관점을 빠르게 익히는 것이 목표입니다.

## 포함 내용

- 현실적인 원천 데이터: 고객 81행(중복 포함), 상품 25행, 주문 501행(중복 포함), 주문상세 약 1,000행, 고객행동 JSONL 180행
- 의도적 품질 이슈: 중복 키, 잘못된 날짜, 고아 외래키, 비정상 할인율·수량, 누락 이메일, 허용되지 않은 등급
- pandas ETL 예제: 타입 변환, 중복 제거, 검증, reject 분리, 조인, 집계
- PostgreSQL 스키마와 upsert 적재
- FastAPI 조회 API와 Vue 3 대시보드
- pytest 기반 핵심 변환 테스트
- 10일 준비 계획, 단계별 요구사항, SQL·ETL 면접 체크리스트

## 가장 빠른 시작

Python 3.11 이상, Node.js 20 이상, Docker가 있다고 가정합니다.

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d db
python -m src.etl.pipeline
uvicorn src.api.main:app --reload --port 8000
```

새 터미널에서 Vue를 실행합니다.

```bash
cd frontend
npm install
npm run dev
```

- API 문서: http://localhost:8000/docs
- Vue 화면: http://localhost:5173
- PostgreSQL: localhost:5432 / `etl_user` / `etl_password`

## DB 없이 먼저 연습하기

```bash
python -m src.etl.preview
pytest -q
```

`preview`는 DB에 쓰지 않고 정제 건수, reject 사유, 고객·월·상품 집계를 출력하고 `data/processed/`에 CSV 결과를 저장합니다.

## 권장 진행 순서

1. `docs/PRACTICE_REQUIREMENTS.md`의 Level 1부터 직접 구현합니다.
2. 막히면 `src/etl/`의 기준 구현과 비교합니다.
3. `sql/interview_queries.sql`을 먼저 직접 작성한 뒤 예시 답안을 확인합니다.
4. `docs/EXPECTED_RESULTS.md`로 핵심 건수와 매출 합계를 대사합니다.
5. `docs/PLAN_10_DAYS.md`에 따라 운영·면접 질문까지 말로 설명합니다.

## 폴더 구조

```text
data/raw/                 원천 CSV·JSONL
data/reference/           코드성 기준정보
data/processed/           preview 실행 결과
src/etl/                  Extract/Transform/Load
src/api/                  FastAPI
sql/                      스키마와 분석 SQL
frontend/                 Vue 3 + Vite 예제
tests/                    변환 로직 테스트
docs/                     실습 요구사항·계획·면접 체크리스트
```

## 완료 기준

- 같은 데이터를 두 번 실행해도 최종 테이블 건수가 변하지 않는다.
- reject 데이터에 원천 파일, 행 식별자, 거절 사유가 남는다.
- 취소·환불 주문을 매출에서 제외한 이유를 설명할 수 있다.
- API 목록에 페이지네이션·정렬·필터가 적용된다.
- Vue에서 월별 매출, 상위 상품, 고객 목록을 확인할 수 있다.
- 장애 시 재실행 지점, 로그·알림, 데이터 정합성 확인 절차를 설명할 수 있다.
