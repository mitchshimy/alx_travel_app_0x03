from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_booking_confirmation_email(user_email, booking_id):
    """
    Sends booking confirmation email to the user.
    """
    subject = "Booking Confirmation"
    message = f"Your booking (ID: {booking_id}) has been confirmed!"
    send_mail(subject, message, 'bookings@alxtravel.com', [user_email])
