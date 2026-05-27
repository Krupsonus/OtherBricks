from tasks.celery_app import celery_app


@celery_app.task(name="tasks.price_aggregator.aggregate_prices")
def aggregate_prices():
    """Fetch prices from external shop APIs and update the database.

    Currently a stub — external API integration is mocked for development.
    """
    pass
