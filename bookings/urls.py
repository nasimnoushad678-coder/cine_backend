from django.urls import path
from .views import (
    create_booking,
    create_payment_intent,
    confirm_payment,
    cancel_booking,
    my_bookings,
)

urlpatterns = [
    path('create/', create_booking),
    path('payment-intent/', create_payment_intent),
    path('confirm-payment/', confirm_payment),
    path('cancel/', cancel_booking),
    path('my-bookings/', my_bookings),
]



