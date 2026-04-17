from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Movie, Theatre, Show, Seat
from .serializers import (
    MovieSerializer,
    TheatreSerializer,
    ShowSerializer,
    SeatSerializer,
)
from .permissions import IsAdminUserCustom

class MovieViewSet(ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAdminUserCustom()]
        return super().get_permissions()

class TheatreViewSet(ModelViewSet):
    queryset = Theatre.objects.all()
    serializer_class = TheatreSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAdminUserCustom()]
        return super().get_permissions()

class ShowViewSet(ModelViewSet):
    queryset = Show.objects.all()
    serializer_class = ShowSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        movie_id = self.request.query_params.get('movie')
        if movie_id:
            return Show.objects.filter(movie_id=movie_id)
        return super().get_queryset()

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAdminUserCustom()]
        return super().get_permissions()

class SeatViewSet(ModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        show_id = self.request.query_params.get('show')
        if show_id:
            return Seat.objects.filter(show_id=show_id)
        return super().get_queryset()

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAdminUserCustom()]
        return super().get_permissions()
