import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in

from .models import User, UserProfile

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):


    def _ensure_profile():
        UserProfile.objects.get_or_create(user=instance)

    if created:
        
        try:
            transaction.on_commit(_ensure_profile)
        except Exception:
           
            _ensure_profile()
    else:
        
        _ensure_profile()



@receiver(user_logged_in)
def notify_staff_first_login(sender, request, user, **kwargs):
    """Send a single notification (to configured recipients) the first time a staff user logs in.

    - Uses an atomic DB update to avoid race conditions (only one notification sent).
    - Email recipients are taken from `settings.STAFF_FIRST_LOGIN_NOTIFY_TO` (iterable of emails)
      or fall back to `settings.ADMINS`.
    - Marks `user.first_login_notified=True` in the database when the notification is scheduled.
    """
 
    if not getattr(user, "is_staff", False):
        return

    updated = User.objects.filter(pk=user.pk, is_staff=True, first_login_notified=False).update(first_login_notified=True)
    if not updated:
       
        return

    def _send():
        recipients = getattr(settings, "STAFF_FIRST_LOGIN_NOTIFY_TO", None)
        if not recipients:
            recipients = [email for _name, email in getattr(settings, "ADMINS", [])]
        if not recipients:
           
            logger.debug("No recipients configured for staff first-login notification")
            return

        subject = getattr(settings, "STAFF_FIRST_LOGIN_SUBJECT", "Staff first-login notification")
        who = user.get_full_name() or user.email or user.admission_number or f"user-{user.pk}"
        message = f"Staff user {who} (role={user.role}) has logged in for the first time."

        try:
            send_mail(subject=subject, message=message, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=list(recipients), fail_silently=False)
        except Exception:
            logger.exception("Failed to send staff first-login notification")

    try:
        transaction.on_commit(_send)
    except Exception:
        _send()
