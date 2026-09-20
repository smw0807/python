# 10일 준비 계획

하루 2~3시간 기준입니다. 7일만 가능하면 1~5일, 7일, 9~10일을 우선 진행하세요.

| 일차 | 핵심 주제 | 실습 | 확인할 결과 |
|---|---|---|---|
| 1일 | Python 데이터 문법 | list/dict comprehension, generator, typing, pathlib, datetime, 예외 처리 | CSV를 읽고 타입을 명시한 함수 3개 작성 |
| 2일 | pandas 기본 | dtype, 결측, 문자열·날짜 정규화, groupby/agg | 고객 중복 제거와 품질 리포트 |
| 3일 | 조인·집계 | merge validate, 주문-상세-상품 조인, 금액 계산 | 고객·월·상품 집계와 독립 합계 검증 |
| 4일 | ETL 설계 | extract/transform/load 분리, 설정·로그·reject | `python -m src.etl.preview` 성공 |
| 5일 | PostgreSQL | DDL, PK/FK/index, explain, upsert, transaction | 동일 배치 2회 실행 후 건수 동일 |
| 6일 | 증분·운영 | watermark, late arrival, backfill, 재시도·알림 | 장애 시나리오 2개 대응 문서화 |
| 7일 | FastAPI | Pydantic, dependency, pagination, 예외 처리 | Swagger에서 5개 API 확인 |
| 8일 | Vue 연동 | fetch, 상태 분리, 필터·페이지, 타입 정의 | 고객·월별·상품 화면 표시 |
| 9일 | 테스트·성능 | pytest, 경계값, SQL EXPLAIN, 대용량 chunk | 핵심 테스트 통과, 병목 1개 설명 |
| 10일 | 면접 리허설 | 아키텍처 3분 설명, 장애·정합성 질문, 라이브 코딩 | 체크리스트의 답을 소리 내어 설명 |

## 매일 반복할 20분 루틴

1. 전날 파이프라인을 처음부터 한 번 실행합니다.
2. 품질 지표 3개와 매출 합계 1개를 확인합니다.
3. 실패 가능 지점 하나와 복구 방법을 말로 설명합니다.
4. pandas 코드 한 곳을 SQL로, SQL 한 곳을 pandas로 바꿔봅니다.

## 면접 직전 3시간 압축 코스

- 45분: `transform.py`를 보지 않고 핵심 정제 재작성
- 45분: 고객별·월별 매출 SQL 작성 및 중복 집계 함정 설명
- 30분: upsert, 트랜잭션, 워터마크, reject 정책 설명
- 30분: FastAPI 페이지네이션과 Vue 로딩·오류 상태 설명
- 30분: 장애 시나리오 1개를 STAR 형식으로 답변
