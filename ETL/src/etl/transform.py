from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

VALID_GRADES = { "BRONZE", "SILVER", "GOLD", "VIP" }
VALID_ORDER_STATUS = { "PAID", "COMPLETED", "CANCELLED", "REFUNDED" }
REVENUE_STATUS = { "PAID", "COMPLETED" }

@dataclass
class TransformResult:
  customers: pd.DataFrame


  def transform_sources(frames: dict[str, pd.DataFrame]) -> TransformResult:
    reject: list[pd.DataFrame] = []

    customers = frames["customers"].copy()
    for col in ["customer_id", "customer_name", "email", "phone", "grade", "city", "marketing_agreed"]:
      customers[col] = customers[col].fillna("").str.strip()