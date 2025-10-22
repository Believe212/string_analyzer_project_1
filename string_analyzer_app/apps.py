# string_analyzer_app/apps.py
from django.apps import AppConfig


class StringAnalyzerAppConfig(AppConfig):
    # This sets the default primary key type for models introduced in Django 3.2+
    default_auto_field = 'django.db.models.BigAutoField'

    # This is the name Django uses internally to refer to your app
    name = 'string_analyzer_app'