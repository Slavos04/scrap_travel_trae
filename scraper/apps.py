from django.apps import AppConfig
import sys


class ScraperConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scraper'
    
    def ready(self):
        # Uruchamiamy scheduler tylko gdy serwer jest uruchamiany, a nie podczas migracji itp.
        if 'runserver' in sys.argv:
            from .tasks import start_scheduler
            start_scheduler()
