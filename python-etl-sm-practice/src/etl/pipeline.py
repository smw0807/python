from datetime import datetime, timezone
import json
import logging
from uuid import uuid4
from sqlalchemy import create_engine, text
from src.config import settings
from src.etl.extract import extract_sources
from src.etl.transform import transform_sources
from src.etl.load import load_result


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    run_id = uuid4()
    started_at = datetime.now(timezone.utc)
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO etl_run(run_id, started_at, status) VALUES (:id, :started, 'RUNNING')"),
                     {"id": run_id, "started": started_at})
    try:
        result = transform_sources(extract_sources(settings.data_dir))
        counts = load_result(engine, run_id, result)
        with engine.begin() as conn:
            conn.execute(text("""
                UPDATE etl_run SET finished_at=:finished, status='SUCCESS',
                  metrics=CAST(:metrics AS JSONB), error_message=NULL WHERE run_id=:id
            """), {"finished": datetime.now(timezone.utc), "metrics": json.dumps({**result.metrics, **counts}), "id": run_id})
        logger.info("ETL completed run_id=%s metrics=%s", run_id, {**result.metrics, **counts})
    except Exception as exc:
        with engine.begin() as conn:
            conn.execute(text("""
                UPDATE etl_run SET finished_at=:finished, status='FAILED', error_message=:message WHERE run_id=:id
            """), {"finished": datetime.now(timezone.utc), "message": str(exc)[:2000], "id": run_id})
        logger.exception("ETL failed run_id=%s", run_id)
        raise


if __name__ == "__main__":
    main()
