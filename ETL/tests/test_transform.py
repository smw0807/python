from pathlib import Path
from src.etl.extract import extract_sources
from src.etl.transform import transform_sources

def result():
  return transform_sources(extract_sources(Path("data/raw")))

def test_duplicate_customer_keeps_latest_version():
  # loc은 특정 인덱스를 가져오는 연산자
  row = result().customers.set_index("customer_id").loc("C0012")
  assert row["grade"] == "VIP"
  assert row["city"] == "서울"

def test_bad_row_are_rejected():
  transformed = result()
  assert transformed.metrics["rejects"] >= 5
  assert "C9999" not in set(transformed.orders["customer_id"])

def test_line_amount_formula_and_bounds():
  items = result().order_items
  assert (items["quantity"] > 0).all()
  assert items["discount_rate"].between(0, 1).all()
  expected = (items["quantity"] * items["unit_price"] * (1 - items["discount_rate"])).round(0)
  assert items["line_amount"].equals(expected)

def test_customer_summary_has_one_row_per_customer():
  summary = result().customer_summary
  assert summary["customer_id"].is_unique
  assert len(summary) == len(result().customers)
  assert summary["total_amount"].sum() > 0