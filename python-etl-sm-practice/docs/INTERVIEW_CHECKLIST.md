# 중급~고급 ETL 면접·실무 체크리스트

## 반드시 설명할 수 있어야 하는 항목

- ETL과 ELT의 선택 기준, 배치와 스트리밍의 경계
- full load와 incremental load의 장단점
- 멱등성, 재시도, 체크포인트, backfill
- 워터마크가 같은 timestamp 레코드를 놓치지 않게 하는 방법
- late-arriving dimension/fact 처리
- SCD Type 1과 Type 2 적용 사례
- 데이터 계약과 스키마 변경 감지
- reject, quarantine, 재처리 정책
- 트랜잭션 경계와 exactly-once가 어려운 이유
- pandas 메모리 절감: dtype, category, chunk, 필요한 컬럼만 읽기
- `merge(validate=...)`와 조인 cardinality 검증
- PostgreSQL index, `EXPLAIN ANALYZE`, composite index 순서
- API pagination, 정렬 whitelist, SQL injection 방지
- 로그·메트릭·알림: 처리량, 지연, reject율, freshness, row count drift

## 자주 나오는 질문과 답변 골격

1. **배치를 재실행해도 안전하게 만들려면?** 자연키/대체키를 정하고 upsert 또는 staging+merge를 사용합니다. 실행 단위 트랜잭션과 run_id를 남기고, 외부 부작용은 별도 멱등 키로 제어합니다.
2. **매출이 갑자기 감소하면?** 인프라 성공 여부만 보지 않고 원천 freshness, 행 수, 상태코드 분포, 조인 손실률, 전일·요일 기준 편차를 순서대로 확인합니다.
3. **pandas가 메모리 부족이면?** 컬럼·행 pushdown, dtype 최적화, chunksize, 중간 컬럼 해제, DB 집계 위임을 검토하고 데이터 크기가 계속 커지면 Spark/Polars 등으로 경계를 정합니다.
4. **중복 제거 기준은?** 단순 `drop_duplicates` 전에 비즈니스 키와 승자 규칙을 합의합니다. 이 예제는 `updated_at` 최신 행을 승자로 사용합니다.
5. **검증을 어디서 하나요?** 입력 스키마, 도메인 규칙, 참조 무결성, 집계 대사, 배포 후 모니터링의 여러 층으로 나눕니다.

## 라이브 코딩 연습

- 고객별 최근 주문 1건 구하기: pandas와 window function 두 방식
- 상품 카테고리별 월 매출과 전월 대비 증감률
- 중복 주문 탐지 및 최신 레코드 선택
- 왼쪽 조인 전후 행 수와 미매칭 비율 검증
- API 정렬 필드를 whitelist로 제한
