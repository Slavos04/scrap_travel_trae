import logging
from datetime import datetime
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .scrapers.scraper_manager import ScraperManager

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('scraper.tasks')


def scrape_travel_offers():
    """Zadanie do scrapowania ofert turystycznych"""
    logger.info("Rozpoczynanie scrapowania ofert turystycznych...")
    
    # Parametry wyszukiwania
    countries = ['Bułgaria', 'Egipt', 'Turcja']
    departure_city = 'Katowice'
    min_date = '2026-05-15'
    duration_range = (5, 8)
    meal_plan = 'all inclusive'
    amenities = ['wifi', 'leżaki']
    
    # Uruchamiamy scrapery
    manager = ScraperManager()
    results = manager.run_all_scrapers(
        countries, 
        departure_city, 
        min_date, 
        duration_range, 
        meal_plan, 
        amenities
    )
    
    logger.info(f"Zakończono scrapowanie ofert turystycznych. Znaleziono {len(results)} ofert.")
    return len(results)


def delete_old_job_executions(max_age=604_800):
    """Usuwa stare wykonania zadań z bazy danych"""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


def start_scheduler():
    """Uruchamia scheduler z zadaniami"""
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    
    # Dodajemy zadanie do codziennego scrapowania ofert (o północy)
    scheduler.add_job(
        scrape_travel_offers,
        trigger=CronTrigger(hour="0", minute="0"),
        id="scrape_travel_offers",
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Dodano zadanie 'scrape_travel_offers' do schedulera.")
    
    # Dodajemy zadanie do czyszczenia starych wykonań zadań (raz w tygodniu)
    scheduler.add_job(
        delete_old_job_executions,
        trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
        id="delete_old_job_executions",
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Dodano zadanie 'delete_old_job_executions' do schedulera.")
    
    try:
        logger.info("Uruchamianie schedulera...")
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Zatrzymywanie schedulera...")
        scheduler.shutdown()
        logger.info("Scheduler zatrzymany!")