from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def send_welcome_mail(sender, instance, created, **kwargs):
    if created:
        subject = "Welcome to Airport!"
        message = "Congratulations, you have successfully registered!"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [instance.email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
