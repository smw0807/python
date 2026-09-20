from pathlib import Path
import json
import pandas as pd


def extract_sources(data_dir: Path) -> dict[str, pd.DataFrame]:
  required = ["customers.csv", "products.csv", "orders.csv", "order_items.csv"]
  missing = [name for name in required if not (data_dir / name).exists()]
  if missing:
    raise FileNotFoundError(f"Missing source files: {', '.join(missing)}")

  frames = {
    "customers": pd.read_csv(data_dir / "customers.csv", dtype=str, encoding="utf-8-sig"),
    "products": pd.read_csv(data_dir / "products.csv", dtype=str, encoding="utf-8-sig"),
    "orders": pd.read_csv(data_dir / "orders.csv", dtype=str, encoding="utf-8-sig"),
    "order_items": pd.read_csv(data_dir / "order_items.csv", dtype=str, encoding="utf-8-sig"),
  }

  events_path = data_dir / "customer_events.jsonl"
  if events_path.exists():
    with events_path.open(encoding="utf-8") as handle:
      frames["events"] = pd.DataFrame(json.loads(line) for line in handle if line.strip())
  return frames