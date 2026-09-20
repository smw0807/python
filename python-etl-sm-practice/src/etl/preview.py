from pathlib import Path

from src.config import settings
from src.etl.extract import extract_sources
from src.etl.transform import transform_sources


def main() -> None:
    result = transform_sources(extract_sources(settings.data_dir))
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    result.customer_summary.to_csv(output_dir / "customer_sales_summary.csv", index=False, encoding="utf-8-sig")
    result.monthly_sales.to_csv(output_dir / "monthly_sales.csv", index=False, encoding="utf-8-sig")
    result.product_sales.to_csv(output_dir / "product_sales.csv", index=False, encoding="utf-8-sig")
    result.rejects.to_csv(output_dir / "rejects.csv", index=False, encoding="utf-8-sig")
    print("quality metrics:", result.metrics)
    print("monthly sales:\n", result.monthly_sales.to_string(index=False))
    print("reject reasons:\n", result.rejects.groupby(["source", "reason"]).size().to_string())


if __name__ == "__main__":
    main()
