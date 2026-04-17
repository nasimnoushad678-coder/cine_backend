from django.db import models
from django.conf import settings
from django.db import models
from movies.models import Show, Seat

class Booking(models.Model):
    STATUS = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    seats = models.ManyToManyField(Seat)
    total_price = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS, default='PENDING')

    stripe_payment_intent = models.CharField(
        max_length=255, blank=True, null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
