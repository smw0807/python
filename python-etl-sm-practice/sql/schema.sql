CREATE TABLE IF NOT EXISTS dim_customer (
  customer_id varchar(20) PRIMARY KEY,
  customer_name varchar(100) NOT NULL,
  email varchar(255), phone varchar(30), grade varchar(20) NOT NULL,
  city varchar(50), joined_at date, marketing_agreed char(1), updated_at timestamp NOT NULL
);
CREATE TABLE IF NOT EXISTS dim_product (
  product_id varchar(20) PRIMARY KEY,
  product_name varchar(200) NOT NULL, category varchar(50) NOT NULL,
  list_price numeric(14,2) NOT NULL, cost_price numeric(14,2) NOT NULL,
  active_yn char(1) NOT NULL, updated_at timestamp NOT NULL
);
CREATE TABLE IF NOT EXISTS fact_order (
  order_id varchar(30) PRIMARY KEY,
  customer_id varchar(20) NOT NULL REFERENCES dim_customer(customer_id),
  ordered_at timestamp NOT NULL, channel varchar(20) NOT NULL, status varchar(20) NOT NULL,
  shipping_fee numeric(14,2) NOT NULL DEFAULT 0, coupon_code varchar(50), updated_at timestamp NOT NULL
);
CREATE TABLE IF NOT EXISTS fact_order_item (
  order_id varchar(30) NOT NULL REFERENCES fact_order(order_id) ON DELETE CASCADE,
  line_no integer NOT NULL, product_id varchar(20) NOT NULL REFERENCES dim_product(product_id),
  quantity integer NOT NULL, unit_price numeric(14,2) NOT NULL,
  discount_rate numeric(6,4) NOT NULL, line_amount numeric(14,2) NOT NULL,
  PRIMARY KEY(order_id, line_no)
);
CREATE TABLE IF NOT EXISTS customer_sales_summary (
  customer_id varchar(20) PRIMARY KEY REFERENCES dim_customer(customer_id),
  customer_name varchar(100) NOT NULL, grade varchar(20) NOT NULL, city varchar(50),
  order_count integer NOT NULL, total_quantity integer NOT NULL,
  total_amount numeric(16,2) NOT NULL, avg_order_amount numeric(16,2) NOT NULL,
  last_order_at timestamp
);
CREATE TABLE IF NOT EXISTS etl_run (
  run_id uuid PRIMARY KEY, started_at timestamptz NOT NULL, finished_at timestamptz,
  status varchar(20) NOT NULL, metrics jsonb, error_message text
);
CREATE TABLE IF NOT EXISTS etl_reject (
  reject_id bigserial PRIMARY KEY, run_id uuid NOT NULL REFERENCES etl_run(run_id),
  source_name varchar(100) NOT NULL, record_key varchar(200), reason text NOT NULL,
  raw_record jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_order_customer_date ON fact_order(customer_id, ordered_at DESC);
CREATE INDEX IF NOT EXISTS idx_order_date_status ON fact_order(ordered_at, status);
CREATE INDEX IF NOT EXISTS idx_item_product ON fact_order_item(product_id);
CREATE INDEX IF NOT EXISTS idx_summary_amount ON customer_sales_summary(total_amount DESC);
