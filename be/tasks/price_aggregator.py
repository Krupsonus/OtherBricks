from database import SessionLocal
from services.aggregator_service import run_aggregation
from tasks.celery_app import celery_app


@celery_app.task(name="tasks.price_aggregator.aggregate_prices", bind=True)
def aggregate_prices(self):
    """Fetch mock prices from external shops, update offers, trigger price alerts."""
    db = SessionLocal()
    try:
        return run_aggregation(db)
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=60, max_retries=3)
    finally:
        db.close()
