import os
from django.apps import AppConfig

class BufferAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'buffer_app'

    def ready(self):
        os.makedirs("media", exist_ok=True)
