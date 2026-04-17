from django.db import models

# Create your models here.
class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.PositiveIntegerField()
    poster = models.URLField()
    release_date = models.DateField()

    def __str__(self):
        return self.title

class Theatre(models.Model):
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Show(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    price = models.PositiveIntegerField()

    class Meta:
        unique_together = ('theatre', 'start_time')

class Seat(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=5)
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('show', 'seat_number')
