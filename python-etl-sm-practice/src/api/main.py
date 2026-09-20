from typing import Literal
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection
from src.config import settings


engine = create_engine(settings.database_url, pool_pre_ping=True)
app = FastAPI(title="Customer Operations API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.api_cors_origins.split(","),
                   allow_methods=["GET"], allow_headers=["*"])


def get_conn():
    with engine.connect() as conn:
        yield conn


@app.get("/health")
def health(conn: Connection = Depends(get_conn)):
    conn.execute(text("SELECT 1"))
    return {"status": "ok"}


SORT_MAP = {
    "total_amount": "total_amount ASC", "-total_amount": "total_amount DESC",
    "last_order_at": "last_order_at ASC NULLS LAST", "-last_order_at": "last_order_at DESC NULLS LAST",
    "customer_id": "customer_id ASC",
}


@app.get("/api/customers")
def customers(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
              grade: str | None = None,
              sort: Literal["total_amount", "-total_amount", "last_order_at", "-last_order_at", "customer_id"] = "-total_amount",
              conn: Connection = Depends(get_conn)):
    where = "WHERE (:grade IS NULL OR grade = :grade)"
    params = {"grade": grade, "limit": page_size, "offset": (page - 1) * page_size}
    total = conn.execute(text(f"SELECT count(*) FROM customer_sales_summary {where}"), params).scalar_one()
    rows = conn.execute(text(f"""
      SELECT customer_id, customer_name, grade, city, order_count, total_amount, avg_order_amount, last_order_at
      FROM customer_sales_summary {where}
      ORDER BY {SORT_MAP[sort]}, customer_id LIMIT :limit OFFSET :offset
    """), params).mappings().all()
    return {"items": [dict(row) for row in rows], "page": page, "page_size": page_size, "total": total}


@app.get("/api/customers/{customer_id}")
def customer(customer_id: str, conn: Connection = Depends(get_conn)):
    row = conn.execute(text("SELECT * FROM customer_sales_summary WHERE customer_id=:id"), {"id": customer_id}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail={"code": "CUSTOMER_NOT_FOUND", "customer_id": customer_id})
    return dict(row)


@app.get("/api/sales/monthly")
def monthly_sales(
    from_month: str = Query("2026-01", pattern=r"^\d{4}-(0[1-9]|1[0-2])$"),
    to_month: str = Query("2026-12", pattern=r"^\d{4}-(0[1-9]|1[0-2])$"),
    conn: Connection = Depends(get_conn),
):
    rows = conn.execute(text("""
      SELECT to_char(date_trunc('month', o.ordered_at), 'YYYY-MM') AS month,
             count(DISTINCT o.order_id) AS order_count,
             count(DISTINCT o.customer_id) AS customer_count,
             sum(i.line_amount) AS total_amount
      FROM fact_order o JOIN fact_order_item i USING(order_id)
      WHERE o.status IN ('PAID','COMPLETED')
        AND o.ordered_at >= to_date(:from_month, 'YYYY-MM')
        AND o.ordered_at < to_date(:to_month, 'YYYY-MM') + interval '1 month'
      GROUP BY 1 ORDER BY 1
    """), {"from_month": from_month, "to_month": to_month}).mappings().all()
    return [dict(row) for row in rows]


@app.get("/api/sales/products")
def product_sales(limit: int = Query(10, ge=1, le=100), category: str | None = None,
                  conn: Connection = Depends(get_conn)):
    rows = conn.execute(text("""
      SELECT p.product_id, p.product_name, p.category, sum(i.quantity) AS total_quantity,
             sum(i.line_amount) AS total_amount,
             sum(i.line_amount - i.quantity * p.cost_price) AS gross_profit
      FROM fact_order o JOIN fact_order_item i USING(order_id) JOIN dim_product p USING(product_id)
      WHERE o.status IN ('PAID','COMPLETED') AND (:category IS NULL OR p.category=:category)
      GROUP BY p.product_id, p.product_name, p.category
      ORDER BY total_amount DESC LIMIT :limit
    """), {"category": category, "limit": limit}).mappings().all()
    return [dict(row) for row in rows]
