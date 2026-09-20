from __future__ import annotations
from dataclasses import dataclass
import pandas as pd


VALID_GRADES = {"BRONZE", "SILVER", "GOLD", "VIP"}
VALID_ORDER_STATUS = {"PAID", "COMPLETED", "CANCELLED", "REFUNDED"}
REVENUE_STATUS = {"PAID", "COMPLETED"}


@dataclass
class TransformResult:
    customers: pd.DataFrame
    products: pd.DataFrame
    orders: pd.DataFrame
    order_items: pd.DataFrame
    rejects: pd.DataFrame
    customer_summary: pd.DataFrame
    monthly_sales: pd.DataFrame
    product_sales: pd.DataFrame
    metrics: dict[str, int]


def _reject(df: pd.DataFrame, mask: pd.Series, source: str, reason: str) -> pd.DataFrame:
    bad = df.loc[mask].copy()
    if bad.empty:
        return pd.DataFrame(columns=["source", "record_key", "reason", "raw_record"])
    key_columns = [c for c in ["customer_id", "product_id", "order_id", "line_no"] if c in bad.columns]
    return pd.DataFrame({
        "source": source,
        "record_key": bad[key_columns].astype(str).agg("/".join, axis=1),
        "reason": reason,
        "raw_record": bad.astype(object).where(pd.notna(bad), None).apply(lambda row: row.to_json(force_ascii=False), axis=1),
    })


def transform_sources(frames: dict[str, pd.DataFrame]) -> TransformResult:
    rejects: list[pd.DataFrame] = []

    customers = frames["customers"].copy()
    for col in ["customer_id", "customer_name", "email", "phone", "grade", "city", "marketing_agreed"]:
        customers[col] = customers[col].fillna("").str.strip()
    customers["grade"] = customers["grade"].str.upper()
    customers["joined_at"] = pd.to_datetime(customers["joined_at"], errors="coerce")
    customers["updated_at"] = pd.to_datetime(customers["updated_at"], errors="coerce")
    bad_customer = customers["customer_id"].eq("") | customers["updated_at"].isna() | ~customers["grade"].isin(VALID_GRADES)
    rejects.append(_reject(customers, bad_customer, "customers.csv", "invalid customer key/date/grade"))
    customers = (customers.loc[~bad_customer]
                 .sort_values(["customer_id", "updated_at"])
                 .drop_duplicates("customer_id", keep="last")
                 .reset_index(drop=True))

    products = frames["products"].copy()
    for col in ["product_id", "product_name", "category", "active_yn"]:
        products[col] = products[col].fillna("").str.strip()
    for col in ["list_price", "cost_price"]:
        products[col] = pd.to_numeric(products[col], errors="coerce")
    products["updated_at"] = pd.to_datetime(products["updated_at"], errors="coerce")
    bad_product = (products["product_id"].eq("") | products["list_price"].lt(0) |
                   products["cost_price"].lt(0) | products["updated_at"].isna())
    rejects.append(_reject(products, bad_product, "products.csv", "invalid product key/price/date"))
    products = (products.loc[~bad_product]
                .sort_values(["product_id", "updated_at"])
                .drop_duplicates("product_id", keep="last")
                .reset_index(drop=True))

    orders = frames["orders"].copy()
    for col in ["order_id", "customer_id", "channel", "status", "coupon_code"]:
        orders[col] = orders[col].fillna("").str.strip()
    orders["status"] = orders["status"].str.upper()
    orders["ordered_at"] = pd.to_datetime(orders["ordered_at"], errors="coerce")
    orders["updated_at"] = pd.to_datetime(orders["updated_at"], errors="coerce")
    orders["shipping_fee"] = pd.to_numeric(orders["shipping_fee"], errors="coerce")
    known_customers = set(customers["customer_id"])
    bad_order = (orders["order_id"].eq("") | orders["ordered_at"].isna() |
                 orders["updated_at"].isna() | ~orders["status"].isin(VALID_ORDER_STATUS) |
                 ~orders["customer_id"].isin(known_customers))
    rejects.append(_reject(orders, bad_order, "orders.csv", "invalid order date/status or orphan customer"))
    orders = (orders.loc[~bad_order]
              .sort_values(["order_id", "updated_at"])
              .drop_duplicates("order_id", keep="last")
              .reset_index(drop=True))

    items = frames["order_items"].copy()
    for col in ["order_id", "product_id"]:
        items[col] = items[col].fillna("").str.strip()
    for col in ["line_no", "quantity", "unit_price", "discount_rate"]:
        items[col] = pd.to_numeric(items[col], errors="coerce")
    known_orders = set(orders["order_id"])
    known_products = set(products["product_id"])
    bad_item = (items["order_id"].eq("") | items["line_no"].isna() | items["quantity"].le(0) |
                items["unit_price"].lt(0) | ~items["discount_rate"].between(0, 1, inclusive="both") |
                ~items["order_id"].isin(known_orders) | ~items["product_id"].isin(known_products))
    rejects.append(_reject(items, bad_item, "order_items.csv", "invalid quantity/price/discount or orphan key"))
    items = items.loc[~bad_item].copy()
    items["line_no"] = items["line_no"].astype(int)
    items["quantity"] = items["quantity"].astype(int)
    items["line_amount"] = (items["quantity"] * items["unit_price"] * (1 - items["discount_rate"])).round(0)
    items = items.drop_duplicates(["order_id", "line_no"], keep="last").reset_index(drop=True)

    valid_orders = orders.loc[orders["status"].isin(REVENUE_STATUS), ["order_id", "customer_id", "ordered_at"]]
    sales = (items.merge(valid_orders, on="order_id", how="inner", validate="many_to_one")
             .merge(products[["product_id", "product_name", "category", "cost_price"]],
                    on="product_id", how="left", validate="many_to_one"))
    sales["month"] = sales["ordered_at"].dt.to_period("M").astype(str)
    sales["gross_profit"] = sales["line_amount"] - sales["quantity"] * sales["cost_price"]

    customer_summary = (sales.groupby("customer_id", as_index=False)
        .agg(order_count=("order_id", "nunique"), total_quantity=("quantity", "sum"),
             total_amount=("line_amount", "sum"), last_order_at=("ordered_at", "max")))
    customer_summary["avg_order_amount"] = (customer_summary["total_amount"] / customer_summary["order_count"]).round(0)
    customer_summary = customers[["customer_id", "customer_name", "grade", "city"]].merge(
        customer_summary, on="customer_id", how="left", validate="one_to_one")
    for col in ["order_count", "total_quantity", "total_amount", "avg_order_amount"]:
        customer_summary[col] = customer_summary[col].fillna(0)
    customer_summary[["order_count", "total_quantity"]] = customer_summary[["order_count", "total_quantity"]].astype(int)

    monthly_sales = (sales.groupby("month", as_index=False)
        .agg(order_count=("order_id", "nunique"), customer_count=("customer_id", "nunique"),
             total_quantity=("quantity", "sum"), total_amount=("line_amount", "sum")))
    monthly_sales["avg_order_amount"] = (monthly_sales["total_amount"] / monthly_sales["order_count"]).round(0)

    product_sales = (sales.groupby(["product_id", "product_name", "category"], as_index=False)
        .agg(total_quantity=("quantity", "sum"), total_amount=("line_amount", "sum"),
             gross_profit=("gross_profit", "sum"))
        .sort_values("total_amount", ascending=False))

    reject_df = pd.concat(rejects, ignore_index=True)
    metrics = {
        "source_customers": len(frames["customers"]), "clean_customers": len(customers),
        "source_orders": len(frames["orders"]), "clean_orders": len(orders),
        "source_order_items": len(frames["order_items"]), "clean_order_items": len(items),
        "rejects": len(reject_df),
    }
    return TransformResult(customers, products, orders, items, reject_df,
                           customer_summary, monthly_sales, product_sales, metrics)
