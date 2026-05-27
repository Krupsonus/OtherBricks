from tasks.celery_app import celery_app


@celery_app.task(name="tasks.email_sender.send_notification_email")
def send_notification_email(notification_id: int):
    """Send an email notification for a price alert or order status change.

    Currently a stub — SMTP integration is mocked for development.
    """
    pass
