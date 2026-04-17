from rest_framework import serializers
from .models import Movie, Theatre, Show, Seat

class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id', 'seat_number', 'is_booked']

class ShowSerializer(serializers.ModelSerializer):
    seats = SeatSerializer(many=True, source='seat_set', read_only=True)

    class Meta:
        model = Show
        fields = ['id', 'movie', 'theatre', 'start_time', 'price', 'seats']

class TheatreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theatre
        fields = '__all__'

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'
