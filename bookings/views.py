import stripe
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Booking
from movies.models import Seat, Show


# 🔐 Stripe setup
stripe.api_key = settings.STRIPE_SECRET_KEY


# 🎟 CREATE BOOKING (NO SEAT BLOCKING HERE)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_booking(request):
    show_id = request.data.get("show_id")
    seat_ids = request.data.get("seat_ids")

    if not show_id or not seat_ids:
        return Response(
            {"error": "show_id and seat_ids required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        show = Show.objects.get(id=show_id)
    except Show.DoesNotExist:
        return Response({"error": "Show not found"}, status=404)

    with transaction.atomic():
        # 🔒 lock seats temporarily (check availability only)
        seats = Seat.objects.select_for_update().filter(
            id__in=seat_ids,
            show=show,
            is_booked=False
        )

        if seats.count() != len(seat_ids):
            return Response(
                {"error": "Some seats already booked"},
                status=status.HTTP_400_BAD_REQUEST
            )

        total_price = show.price * len(seat_ids)

        booking = Booking.objects.create(
            user=request.user,
            show=show,
            total_price=total_price,
            status='PENDING'
        )

        booking.seats.set(seats)

    return Response({
        "id": booking.id,
        "message": "Booking created",
        "total_price": booking.total_price
    }, status=status.HTTP_201_CREATED)


# ❌ CANCEL BOOKING (ONLY BEFORE 3 HOURS)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking(request):
    booking_id = request.data.get("booking_id")

    try:
        booking = Booking.objects.get(
            id=booking_id,
            user=request.user
        )
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)

    if booking.status != "PAID":
        return Response({"error": "Only paid bookings can be cancelled"}, status=400)

    show_time = booking.show.start_time
    now = timezone.now()

    # ⏱ 3-hour rule
    if show_time - now < timedelta(hours=3):
        return Response(
            {"error": "Cannot cancel within 3 hours of show"},
            status=400
        )

    with transaction.atomic():
        seats = booking.seats.select_for_update()
        seats.update(is_booked=False)

        booking.status = "CANCELLED"
        booking.save()

    return Response({"message": "Booking cancelled successfully"})


# 💳 CREATE STRIPE PAYMENT INTENT
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_intent(request):
    booking_id = request.data.get("booking_id")

    try:
        booking = Booking.objects.get(
            id=booking_id,
            user=request.user,
            status='PENDING'
        )
    except Booking.DoesNotExist:
        return Response({"error": "Invalid booking"}, status=404)

    try:
        intent = stripe.PaymentIntent.create(
            amount=booking.total_price * 100,  # paise
            currency="inr",
            metadata={"booking_id": booking.id},
        )
    except Exception as e:
        return Response({"error": str(e)}, status=500)

    booking.stripe_payment_intent = intent.id
    booking.save()

    return Response({
        "client_secret": intent.client_secret
    })


# ✅ CONFIRM PAYMENT & BLOCK SEATS
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_payment(request):
    booking_id = request.data.get("booking_id")

    try:
        booking = Booking.objects.get(
            id=booking_id,
            user=request.user,
            status='PENDING'
        )
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)

    if not booking.stripe_payment_intent:
        return Response({"error": "No payment intent found"}, status=400)

    try:
        intent = stripe.PaymentIntent.retrieve(
            booking.stripe_payment_intent
        )
    except Exception as e:
        return Response({"error": str(e)}, status=500)

    if intent.status == "succeeded":

        with transaction.atomic():
            seats = booking.seats.select_for_update()

            # ❗ check again to avoid race condition
            if seats.filter(is_booked=True).exists():
                return Response({"error": "Seats already booked"}, status=400)

            # ✅ NOW block seats
            seats.update(is_booked=True)

            booking.status = "PAID"
            booking.save()

        return Response({"message": "Payment successful"})

    return Response({"error": "Payment not completed"}, status=400)


# 🎟 GET USER BOOKINGS (TICKET PAGE)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-id')

    data = []

    for b in bookings:
        seats = [s.seat_number for s in b.seats.all()]

        data.append({
            "id": b.id,
            "movie": b.show.movie.title,
            "theatre": b.show.theatre.name,
            "time": b.show.start_time,
            "seats": seats,
            "status": b.status,
            "total_price": b.total_price
        })

    return Response(data)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-id')

    data = []

    for b in bookings:
        seats = [s.seat_number for s in b.seats.all()]

        data.append({
            "id": b.id,
            "movie": b.show.movie.title,
            "theatre": b.show.theatre.name,
            "time": b.show.start_time,
            "seats": seats,
            "status": b.status,
            "total_price": b.total_price
        })

    return Response(data)