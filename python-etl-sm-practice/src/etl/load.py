from __future__ import annotations
from uuid import UUID
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


def _records(df: pd.DataFrame) -> list[dict]:
    def normalize(value):
        if pd.isna(value):
            return None
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime()
        if hasattr(value, "item"):
            return value.item()
        return value

    return [{key: normalize(value) for key, value in row.items()} for row in df.to_dict(orient="records")]


def load_result(engine: Engine, run_id: UUID, result) -> dict[str, int]:
    counts: dict[str, int] = {}
    with engine.begin() as conn:
        customer_sql = text("""
            INSERT INTO dim_customer (customer_id, customer_name, email, phone, grade, city, joined_at, marketing_agreed, updated_at)
            VALUES (:customer_id, :customer_name, NULLIF(:email,''), :phone, :grade, :city, :joined_at, :marketing_agreed, :updated_at)
            ON CONFLICT (customer_id) DO UPDATE SET
              customer_name=EXCLUDED.customer_name, email=EXCLUDED.email, phone=EXCLUDED.phone,
              grade=EXCLUDED.grade, city=EXCLUDED.city, joined_at=EXCLUDED.joined_at,
              marketing_agreed=EXCLUDED.marketing_agreed, updated_at=EXCLUDED.updated_at
            WHERE dim_customer.updated_at <= EXCLUDED.updated_at
        """)
        conn.execute(customer_sql, _records(result.customers))
        counts["customers"] = len(result.customers)

        product_sql = text("""
            INSERT INTO dim_product (product_id, product_name, category, list_price, cost_price, active_yn, updated_at)
            VALUES (:product_id, :product_name, :category, :list_price, :cost_price, :active_yn, :updated_at)
            ON CONFLICT (product_id) DO UPDATE SET
              product_name=EXCLUDED.product_name, category=EXCLUDED.category,
              list_price=EXCLUDED.list_price, cost_price=EXCLUDED.cost_price,
              active_yn=EXCLUDED.active_yn, updated_at=EXCLUDED.updated_at
            WHERE dim_product.updated_at <= EXCLUDED.updated_at
        """)
        conn.execute(product_sql, _records(result.products))
        counts["products"] = len(result.products)

        order_sql = text("""
            INSERT INTO fact_order (order_id, customer_id, ordered_at, channel, status, shipping_fee, coupon_code, updated_at)
            VALUES (:order_id, :customer_id, :ordered_at, :channel, :status, :shipping_fee, NULLIF(:coupon_code,''), :updated_at)
            ON CONFLICT (order_id) DO UPDATE SET
              customer_id=EXCLUDED.customer_id, ordered_at=EXCLUDED.ordered_at, channel=EXCLUDED.channel,
              status=EXCLUDED.status, shipping_fee=EXCLUDED.shipping_fee,
              coupon_code=EXCLUDED.coupon_code, updated_at=EXCLUDED.updated_at
            WHERE fact_order.updated_at <= EXCLUDED.updated_at
        """)
        conn.execute(order_sql, _records(result.orders))
        counts["orders"] = len(result.orders)

        item_sql = text("""
            INSERT INTO fact_order_item (order_id, line_no, product_id, quantity, unit_price, discount_rate, line_amount)
            VALUES (:order_id, :line_no, :product_id, :quantity, :unit_price, :discount_rate, :line_amount)
            ON CONFLICT (order_id, line_no) DO UPDATE SET
              product_id=EXCLUDED.product_id, quantity=EXCLUDED.quantity,
              unit_price=EXCLUDED.unit_price, discount_rate=EXCLUDED.discount_rate,
              line_amount=EXCLUDED.line_amount
        """)
        conn.execute(item_sql, _records(result.order_items))
        counts["order_items"] = len(result.order_items)

        conn.execute(text("DELETE FROM customer_sales_summary"))
        summary_sql = text("""
            INSERT INTO customer_sales_summary
              (customer_id, customer_name, grade, city, order_count, total_quantity, total_amount, avg_order_amount, last_order_at)
            VALUES
              (:customer_id, :customer_name, :grade, :city, :order_count, :total_quantity, :total_amount, :avg_order_amount, :last_order_at)
        """)
        conn.execute(summary_sql, _records(result.customer_summary))
        counts["customer_sales_summary"] = len(result.customer_summary)

        reject_sql = text("""
            INSERT INTO etl_reject (run_id, source_name, record_key, reason, raw_record)
            VALUES (:run_id, :source, :record_key, :reason, CAST(:raw_record AS JSONB))
        """)
        if not result.rejects.empty:
            payload = [{**row, "run_id": run_id, "raw_record": row["raw_record"]} for row in _records(result.rejects)]
            conn.execute(reject_sql, payload)
        counts["rejects"] = len(result.rejects)
    return counts
