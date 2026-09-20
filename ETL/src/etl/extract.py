from pathlib import Path
import json
import pandas as pd


"""
Extracts source data from the data directory.
"""
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
    # with 문을 사용하면 파일을 열고 자동으로 닫힙니다.
    with events_path.open(encoding="utf-8") as handle:
      # json.loads() 함수를 사용하여 각 줄을 JSON 형식으로 파싱하고, 빈 줄은 제외합니다.
      # strip() 함수를 사용하여 줄의 양쪽 공백을 제거합니다.
      frames["events"] = pd.DataFrame(json.loads(line) for line in handle if line.strip())
  return frames