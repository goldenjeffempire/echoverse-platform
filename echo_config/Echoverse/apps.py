from django.apps import AppConfig


class EchoverseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Echoverse'

    def ready(self):
        import Echoverse.signals
git add .
git commit -m "Added email verification for user registration"
