from rest_framework.routers import DefaultRouter
from .views import MovieViewSet, TheatreViewSet, ShowViewSet, SeatViewSet

router = DefaultRouter()
router.register('movies', MovieViewSet)
router.register('theatres', TheatreViewSet)
router.register('shows', ShowViewSet)
router.register('seats', SeatViewSet)

urlpatterns = router.urls
