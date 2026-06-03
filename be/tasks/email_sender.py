from datetime import datetime, timezone

from tasks.celery_app import celery_app


@celery_app.task(name="tasks.email_sender.send_notification_email")
def send_notification_email(notification_id: int):
    """Mark a notification as sent and log the mock email.

    SMTP integration is mocked — in production this would send a real email.
    """
    from database import SessionLocal
    from models.notification import Notification

    db = SessionLocal()
    try:
        notif = db.query(Notification).filter(Notification.id == notification_id).first()
        if notif and not notif.is_sent:
            notif.is_sent = True
            notif.sent_at = datetime.now(timezone.utc)
            db.commit()
            print(f"[mock email] Notification #{notification_id} sent to user {notif.user_id}: {notif.message}")
    finally:
        db.close()
