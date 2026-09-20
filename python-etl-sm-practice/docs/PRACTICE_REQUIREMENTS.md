# 단계별 실습 요구사항

먼저 직접 구현한 뒤 `src/etl/`의 기준 구현과 비교하세요. 각 단계는 독립 과제가 아니라 하나의 운영 파이프라인으로 이어집니다.

## Level 1. pandas 정제

입력: `customers.csv`, `products.csv`, `orders.csv`, `order_items.csv`

1. 문자열 앞뒤 공백과 대소문자를 정규화합니다.
2. 날짜를 `datetime64`로 변환하고 변환 실패 행을 reject로 분리합니다.
3. 고객·주문 중복은 `updated_at`이 가장 최신인 행만 남깁니다.
4. 고객 등급은 `BRONZE/SILVER/GOLD/VIP`만 허용합니다.
5. 주문상세는 `quantity > 0`, `0 <= discount_rate <= 1`, `unit_price >= 0`을 검증합니다.
6. 고객이 없는 주문과 상품이 없는 주문상세는 고아 레코드로 분리합니다.
7. `line_amount = quantity * unit_price * (1 - discount_rate)`를 계산합니다. 금액 반올림 규칙을 명시합니다.

산출물: 정제된 DataFrame 4개, reject DataFrame 1개, 품질 지표 딕셔너리.

## Level 2. 데이터 마트 집계

매출 인정 상태는 `PAID`, `COMPLETED`로 정의합니다.

- 고객 요약: 주문 수, 구매 수량, 총 매출, 최근 주문일, 평균 주문금액
- 월별 매출: 월, 주문 수, 고객 수, 매출, 객단가
- 상품 매출: 상품·카테고리별 수량, 매출, 매출총이익
- 고객 세그먼트: RFM 기준을 직접 정의하고 등급과 비교

검증 질문:

- 주문 수를 `count`와 `nunique` 중 무엇으로 계산해야 하나요?
- 주문 헤더와 상세를 조인한 뒤 배송비를 합산하면 왜 중복될 수 있나요?
- 취소·환불이 다음 달에 발생하면 어느 월의 매출을 수정해야 하나요?

## Level 3. PostgreSQL 적재

`sql/schema.sql`을 실행하고 다음을 구현합니다.

- 차원·팩트 테이블 PK/FK/인덱스
- `INSERT ... ON CONFLICT DO UPDATE` 기반 멱등 upsert
- 한 실행 단위 트랜잭션
- `etl_run`에 시작·종료·상태·추출·적재·reject 건수 기록
- reject 원문과 사유 보존
- 중간 실패 후 재실행해도 중복이 생기지 않는지 확인

심화: 증분 추출 워터마크(`updated_at`), 지연 도착 데이터, 배치 재처리 구간을 설계하세요.

## Level 4. FastAPI

필수 API:

- `GET /health`
- `GET /api/customers?page=1&page_size=20&grade=VIP&sort=-total_amount`
- `GET /api/customers/{customer_id}`
- `GET /api/sales/monthly?from_month=2026-01&to_month=2026-09`
- `GET /api/sales/products?limit=10&category=DIGITAL`

요구사항: Pydantic 응답 모델, 입력값 검증, 일관된 오류 응답, 페이지네이션 메타데이터, 쿼리 파라미터 바인딩, N+1 방지.

## Level 5. Vue 연동

- 로딩·오류·빈 데이터 상태를 구분합니다.
- 월별 매출과 상위 상품을 표로 표시합니다.
- 고객 등급 필터와 페이지 이동을 구현합니다.
- API base URL은 환경 변수로 관리합니다.
- 금액·날짜 표시는 프런트에서 포맷하되 원본 API 타입은 숫자·ISO 날짜를 유지합니다.

## 운영 장애 시나리오

아래 상황에 대해 탐지, 영향 범위, 즉시 조치, 근본 조치, 재발 방지를 각각 작성하세요.

1. 원천 CSV 컬럼명이 예고 없이 변경됨
2. 같은 주문이 10배로 중복 유입됨
3. 배치가 상품 적재 후 주문 적재 전에 종료됨
4. 전일 대비 매출이 70% 감소했지만 오류 로그는 없음
5. API 응답이 데이터 증가 후 5초 이상 걸림
