# 직접 타이핑용 작업 순서

목표는 완성 코드를 한꺼번에 복사하는 것이 아니라, 작은 단위로 직접 작성하고 매 단계에서 실행 결과를 확인하는 것입니다. `data/`의 샘플 데이터는 직접 입력하지 말고 그대로 사용하세요. Python, SQL, Vue 코드만 직접 타이핑하는 것을 권장합니다.

## 0단계. 빈 연습 프로젝트 만들기

아래 구조만 먼저 만듭니다.

```text
customer-etl-practice/
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── etl/
│   └── api/
├── sql/
├── tests/
└── frontend/
```

제공된 패키지에서 다음 파일만 새 프로젝트로 복사합니다.

```text
data/raw/customers.csv
data/raw/products.csv
data/raw/orders.csv
data/raw/order_items.csv
data/raw/customer_events.jsonl
data/reference/channel_codes.csv
```

그다음 가상환경과 의존성을 준비합니다.

```bash
python -m venv .venv
source .venv/bin/activate
pip install pandas pytest sqlalchemy "psycopg[binary]" fastapi "uvicorn[standard]"
```

체크포인트: `python --version`과 `python -c "import pandas; print(pandas.__version__)"`이 정상 출력되어야 합니다.

## 1단계. Extract부터 작성하기

작성 파일: `src/etl/extract.py`

처음에는 함수 하나만 만듭니다.

```python
def extract_sources(data_dir: Path) -> dict[str, pd.DataFrame]:
    ...
```

진행 순서:

1. `customers.csv` 하나만 읽습니다.
2. 컬럼명과 상위 5행을 출력합니다.
3. 나머지 CSV 세 개를 추가합니다.
4. 필수 파일이 없을 때 `FileNotFoundError`를 발생시킵니다.
5. 마지막에 JSONL을 추가합니다.

임시 확인 코드:

```bash
python -c "from pathlib import Path; from src.etl.extract import extract_sources; print({k: len(v) for k, v in extract_sources(Path('data/raw')).items()})"
```

기대 결과: 고객 81행, 상품 25행, 주문 501행, 주문상세 1,243행, 이벤트 180행.

## 2단계. 고객 데이터만 정제하기

작성 파일: `src/etl/transform.py`

전체 변환을 한꺼번에 만들지 말고 고객부터 시작합니다.

1. 원본 DataFrame을 `copy()`합니다.
2. 문자열의 공백을 제거합니다.
3. `grade`를 대문자로 통일합니다.
4. 날짜 컬럼을 `pd.to_datetime(..., errors="coerce")`로 변환합니다.
5. 허용 등급을 상수로 정의합니다.
6. 잘못된 등급과 날짜를 reject로 분리합니다.
7. `updated_at`으로 정렬한 후 최신 고객만 남깁니다.

체크포인트:

- `C0055`는 허용되지 않은 등급이므로 제외됩니다.
- `C0012`는 중복 중 최신 행이 남고 등급은 `VIP`입니다.
- 정제 고객은 79명입니다.

여기까지 끝난 뒤에만 상품 정제를 추가합니다.

## 3단계. 상품·주문·주문상세 정제하기

다음 순서로 한 종류씩 추가합니다.

### 3-1. 상품

- 판매가와 원가를 숫자로 변환합니다.
- 음수 가격과 잘못된 수정일을 검사합니다.
- `product_id` 중복 시 최신 행을 남깁니다.

### 3-2. 주문

- 주문일과 수정일을 날짜로 변환합니다.
- 상태값을 검사합니다.
- 정제 고객에 없는 `customer_id`를 찾습니다.
- 주문 중복은 최신 `updated_at`을 남깁니다.

체크포인트: 잘못된 날짜의 `O000287`과 고아 고객 주문 `O000333`이 제외되어야 합니다.

### 3-3. 주문상세

- 수량, 단가, 할인율을 숫자로 변환합니다.
- 수량은 0보다 커야 합니다.
- 할인율은 0 이상 1 이하여야 합니다.
- 정제 주문과 상품에 없는 키를 검사합니다.
- `line_amount`를 계산합니다.

```python
line_amount = quantity * unit_price * (1 - discount_rate)
```

체크포인트: 정제 주문 493행, 주문상세 1,209행, 전체 reject 42행.

## 4단계. 집계 만들기

취소와 환불을 제외하고 `PAID`, `COMPLETED`만 인정 매출로 사용합니다.

아래 순서로 만드세요.

1. 주문상세와 유효 주문을 `many_to_one`으로 조인합니다.
2. 상품 정보를 `many_to_one`으로 조인합니다.
3. 고객별 집계를 만듭니다.
4. 월별 집계를 만듭니다.
5. 상품별 집계를 만듭니다.

`merge(validate="many_to_one")`를 반드시 사용해 조인 관계가 예상과 다른 경우 즉시 실패하게 만드세요.

체크포인트: 2026년 1~9월 인정 매출 합계는 `96,104,600원`입니다.

## 5단계. DB 없는 실행 파일 만들기

작성 파일: `src/config.py`, `src/etl/preview.py`

`preview.py`에서 다음 순서로 호출합니다.

```text
extract_sources
→ transform_sources
→ 품질 지표 출력
→ data/processed에 CSV 저장
```

실행:

```bash
python -m src.etl.preview
```

이 단계가 완전히 동작하기 전에는 PostgreSQL로 넘어가지 않는 것을 권장합니다.

## 6단계. 변환 테스트 작성하기

작성 파일: `tests/test_transform.py`

기준 구현을 보지 않고 다음 테스트를 먼저 작성해 보세요.

1. `C0012`의 최신 버전이 선택되는가?
2. `C9999` 주문이 제거되는가?
3. 수량과 할인율이 허용 범위 안에 있는가?
4. 계산한 `line_amount`가 공식과 일치하는가?
5. 고객 요약이 고객당 한 행인가?

실행:

```bash
pytest -q
```

실패하면 코드를 바로 고치기 전에 어떤 업무 규칙이 깨졌는지 한 문장으로 설명하세요.

## 7단계. PostgreSQL 스키마 작성하기

작성 순서:

1. `docker-compose.yml`
2. `sql/schema.sql`
3. 고객·상품 차원 테이블
4. 주문·주문상세 팩트 테이블
5. 고객 매출 요약 테이블
6. ETL 실행 이력과 reject 테이블
7. 조회용 인덱스

실행:

```bash
docker compose up -d db
```

PK, FK, 복합키, 인덱스를 왜 그렇게 정했는지 말로 설명할 수 있어야 합니다.

## 8단계. Load와 전체 파이프라인 작성하기

작성 파일: `src/etl/load.py`, `src/etl/pipeline.py`

순서:

1. 고객만 upsert합니다.
2. 같은 배치를 두 번 실행해 고객 수가 늘지 않는지 봅니다.
3. 상품, 주문, 주문상세 순서로 확장합니다.
4. 하나의 트랜잭션으로 묶습니다.
5. 마지막에 요약 테이블과 reject를 적재합니다.
6. `etl_run`에 `RUNNING`, `SUCCESS`, `FAILED`를 기록합니다.

```bash
python -m src.etl.pipeline
python -m src.etl.pipeline
```

체크포인트: 두 번째 실행 후에도 비즈니스 테이블 건수가 첫 번째 실행과 같아야 합니다.

## 9단계. SQL 문제를 직접 풀기

`sql/interview_queries.sql`은 처음부터 열지 마세요. 아래 문제를 먼저 별도 파일에 작성합니다.

1. 고객별 최근 주문 한 건
2. 월별 매출과 전월 대비 증감률
3. 주문은 있지만 상세가 없는 데이터
4. 등급별 매출 상위 3명
5. ETL 실행 성공률과 평균 reject 수

작성 후 제공된 SQL과 결과뿐 아니라 동률, NULL, 중복 처리 방식도 비교합니다.

## 10단계. FastAPI 작성하기

작성 파일: `src/api/main.py`

한 번에 API 다섯 개를 만들지 말고 다음 순서로 진행합니다.

1. `/health`
2. `/api/customers/{customer_id}`
3. `/api/customers` 목록과 페이지네이션
4. 월별 매출
5. 상품별 매출
6. 필터, 정렬 whitelist, 404 오류 형식

```bash
uvicorn src.api.main:app --reload --port 8000
```

브라우저에서 `http://localhost:8000/docs`로 각 API를 직접 호출합니다.

## 11단계. Vue 화면 작성하기

화면은 다음 순서가 안전합니다.

1. Vite Vue TypeScript 프로젝트 생성
2. `api.ts`에 타입과 공통 `get` 함수 작성
3. 고객 목록만 출력
4. 로딩, 오류, 빈 데이터 상태 분리
5. 등급 필터와 페이지 이동
6. 월별 매출과 상품 매출 추가
7. 마지막에 스타일 적용

처음부터 차트 라이브러리를 추가하지 말고 표로 데이터가 정확히 보이는지 먼저 확인하세요.

## 12단계. 운영 관점 보강하기

마지막으로 다음 상황을 직접 만들어 봅니다.

- 원천 파일 하나의 이름을 바꿔 실패시키기
- 같은 배치를 두 번 실행하기
- 주문 컬럼 하나를 삭제해 스키마 변경 재현하기
- 할인율 오류를 100건 추가해 reject 급증 재현하기
- 고객 목록을 10만 건으로 늘려 API 응답시간 확인하기

각 실험마다 `탐지 → 영향 → 즉시 조치 → 재처리 → 재발 방지` 순서로 메모하면 면접 답변 재료가 됩니다.

## 기준 구현을 보는 시점

- 20~30분 고민해도 문법 때문에 진행하지 못할 때 해당 함수만 봅니다.
- 결과가 다르면 먼저 `docs/EXPECTED_RESULTS.md`와 건수를 비교합니다.
- 완성 파일 전체를 복사하지 말고, 차이가 난 이유를 적은 후 다시 직접 타이핑합니다.
- 하루가 끝날 때만 제공 코드와 구조를 비교합니다.
