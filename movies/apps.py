from django.apps import AppConfig
from django.apps import AppConfig

class MoviesConfig(AppConfig):
    name = 'movies'
class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movies'

    def ready(self):
        import movies.signals