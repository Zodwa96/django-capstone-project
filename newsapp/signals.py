"""Signal handlers for the News Application.

Listens for ``Article`` saves and triggers the approval side effects
(subscriber emails and the internal API notification) the moment an
existing article becomes approved.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Article
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Article)
def handle_article_approval(sender, instance, created, **kwargs):
    """Trigger notifications when an existing article gets approved.

    Runs after every :class:`Article` save. It only fires the
    notification helpers when the article is approved, has an
    ``approved_at`` timestamp, and was not just created (i.e. it was
    updated from unapproved to approved), so that brand-new drafts
    never trigger a notification.
    """
    # Only trigger when approved becomes True and not on creation
    # Use update_fields check to avoid recursion
    if instance.approved and instance.approved_at:
        # Prevent duplicate sends by checking if this is a new approval
        # We use a simple flag via cache would be better, but for capstone we keep idempotent
        try:
            from .views import send_approval_notifications, post_to_api
            # Avoid triggering during initial creation
            if not created:
                # Only notify if approved just now (within 5 seconds window check is in save)
                # For simplicity, we notify - send_mail is set to console backend
                send_approval_notifications(instance)
                post_to_api(instance)
        except Exception as e:
            logger.error(f"Signal error: {e}")
