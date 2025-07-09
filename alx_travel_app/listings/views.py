from rest_framework import viewsets
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
import os
import requests
from .tasks import send_booking_confirmation_email

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        send_booking_confirmation_email.delay(self.request.user.email, booking.id)

CHAPA_URL = "https://api.chapa.co/v1"

@api_view(['POST'])
def initiate_payment(request):
    data = request.data
    chapa_key = os.getenv("CHAPA_SECRET_KEY")

    payload = {
        "amount": data["amount"],
        "currency": "ETB",
        "email": data["email"],
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "tx_ref": data["booking_reference"],
        "callback_url": "https://your-domain.com/verify-payment/",
        "return_url": "https://your-domain.com/payment-success/",
        "customization[title]": "Booking Payment"
    }

    headers = {"Authorization": f"Bearer {chapa_key}"}

    res = requests.post(f"{CHAPA_URL}/transaction/initialize", json=payload, headers=headers)

    if res.status_code == 200:
        response_data = res.json()
        Payment.objects.create(
            booking_reference=data["booking_reference"],
            amount=data["amount"],
            status="Pending",
            transaction_id=data["booking_reference"]  # Fix: use the same tx_ref sent
        )
        return Response({"payment_url": response_data['data']['checkout_url']})
    else:
        return Response(res.json(), status=res.status_code)

@api_view(['GET'])
def verify_payment(request):
    tx_ref = request.GET.get("tx_ref")
    chapa_key = os.getenv("CHAPA_SECRET_KEY")

    res = requests.get(f"{CHAPA_URL}/transaction/verify/{tx_ref}", headers={
        "Authorization": f"Bearer {chapa_key}"
    })

    if res.status_code == 200:
        payment_data = res.json()
        status = payment_data["data"]["status"]
        payment = get_object_or_404(Payment, transaction_id=tx_ref)

        if status == "success":
            payment.status = "Completed"
        else:
            payment.status = "Failed"
        payment.save()

        return Response({"message": "Payment status updated", "status": status})
    else:
        return Response(res.json(), status=res.status_code)
