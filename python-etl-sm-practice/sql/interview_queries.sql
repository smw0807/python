-- 1. 고객별 최근 주문 1건: 동률 규칙을 order_id DESC로 명시
SELECT customer_id, order_id, ordered_at, status
FROM (
  SELECT o.*, row_number() OVER (
    PARTITION BY customer_id ORDER BY ordered_at DESC, order_id DESC
  ) AS rn
  FROM fact_order o
) ranked
WHERE rn = 1;

-- 2. 월별 매출과 전월 대비 증감률. 배송비는 상세 조인에 섞지 않았다.
WITH monthly AS (
  SELECT date_trunc('month', o.ordered_at)::date AS month,
         count(DISTINCT o.order_id) AS orders,
         sum(i.line_amount) AS revenue
  FROM fact_order o
  JOIN fact_order_item i USING (order_id)
  WHERE o.status IN ('PAID', 'COMPLETED')
  GROUP BY 1
)
SELECT month, orders, revenue,
       round((revenue / nullif(lag(revenue) OVER (ORDER BY month), 0) - 1) * 100, 1) AS mom_pct
FROM monthly ORDER BY month;

-- 3. 조인으로 유실되는 주문 탐지
SELECT o.order_id, o.customer_id
FROM fact_order o
LEFT JOIN fact_order_item i USING (order_id)
WHERE i.order_id IS NULL;

-- 4. 등급별 상위 3명
SELECT * FROM (
  SELECT s.*, dense_rank() OVER (PARTITION BY grade ORDER BY total_amount DESC) AS rnk
  FROM customer_sales_summary s
) x WHERE rnk <= 3 ORDER BY grade, rnk, customer_id;

-- 5. 실행 품질 추이
SELECT started_at::date AS run_date, status, count(*) AS runs,
       avg((metrics->>'rejects')::numeric) AS avg_rejects
FROM etl_run GROUP BY 1, 2 ORDER BY 1 DESC, 2;
