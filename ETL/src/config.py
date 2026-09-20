import os
from dataclasses import dataclass
from pathlib import Path

def _load_env_file(path: Path = Path(".env")) -> None:
  if not path.exists():
    return
  for line in path.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
      continue
    key, value = line.split("=", 1)
    # strip("\"'")은 문자열 양쪽의 따옴표와 작은 따옴표를 제거하는 연산자
    os.environ.setdefault(key.strip(), value.strip().strip("\"'"))

_load_env_file()

@dataclass(frozen=True)
class Settings:
  database_url: str = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://etl_user:etl_password@localhost:5432/customer_dw",
  )
  data_dir: Path = Path(os.getenv("DATA_DIR", "data/raw"))
  api_cors_origins: str = os.getenv("API_CORS_ORIGINS", "http://localhost:5173")

settings = Settings()