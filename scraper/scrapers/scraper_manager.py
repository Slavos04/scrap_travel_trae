import logging
from django.utils import timezone
from django.db import transaction
from ..models import Destination, TravelAgency, TravelOffer
from .travelplanet_scraper import TravelplanetScraper
from .wakacje_scraper import WakacjeScraper
from .fly_scraper import FlyScraper

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('scraper.manager')


class ScraperManager:
    """Klasa zarządzająca wszystkimi scraperami i zapisująca dane do bazy"""
    
    def __init__(self):
        self.scrapers = [
            TravelplanetScraper(),
            WakacjeScraper(),
            FlyScraper()
        ]
        self.logger = logger
    
    def run_all_scrapers(self, countries=None, departure_city='Katowice', min_date='2026-05-15', 
                        duration_range=(5, 8), meal_plan='all inclusive', amenities=None):
        """Uruchamia wszystkie scrapery i zapisuje wyniki do bazy danych"""
        if countries is None:
            countries = ['Bułgaria', 'Egipt', 'Turcja']
        
        if amenities is None:
            amenities = ['wifi', 'leżaki']
        
        all_results = []
        
        for scraper in self.scrapers:
            try:
                self.logger.info(f"Uruchamianie scrapera dla {scraper.agency_name}")
                results = scraper.search_offers(
                    countries, 
                    departure_city, 
                    min_date, 
                    duration_range, 
                    meal_plan, 
                    amenities
                )
                
                self.logger.info(f"Scraper {scraper.agency_name} znalazł {len(results)} ofert")
                all_results.extend([(scraper.agency_name, scraper.agency_url, result) for result in results])
                
            except Exception as e:
                self.logger.error(f"Błąd podczas uruchamiania scrapera {scraper.agency_name}: {e}")
        
        self.logger.info(f"Łącznie znaleziono {len(all_results)} ofert")
        
        # Zapisujemy wyniki do bazy danych
        self.save_results_to_db(all_results)
        
        return all_results
    
    @transaction.atomic
    def save_results_to_db(self, results):
        """Zapisuje wyniki do bazy danych"""
        self.logger.info("Zapisywanie wyników do bazy danych...")
        
        # Słowniki do przechowywania już utworzonych obiektów, aby uniknąć duplikatów
        destinations = {}
        agencies = {}
        
        offers_count = 0
        
        for agency_name, agency_url, offer_data in results:
            try:
                # Pobieramy lub tworzymy agencję
                if agency_name not in agencies:
                    agency, created = TravelAgency.objects.get_or_create(
                        name=agency_name,
                        defaults={'website': agency_url}
                    )
                    agencies[agency_name] = agency
                else:
                    agency = agencies[agency_name]
                
                # Pobieramy lub tworzymy destynację
                destination_key = f"{offer_data['destination_name']}-{offer_data['country']}"
                if destination_key not in destinations:
                    destination, created = Destination.objects.get_or_create(
                        name=offer_data['destination_name'],
                        country=offer_data['country']
                    )
                    destinations[destination_key] = destination
                else:
                    destination = destinations[destination_key]
                
                # Tworzymy lub aktualizujemy ofertę
                offer, created = TravelOffer.objects.update_or_create(
                    hotel_name=offer_data['hotel_name'],
                    destination=destination,
                    agency=agency,
                    departure_date=offer_data['departure_date'],
                    return_date=offer_data['return_date'],
                    departure_city=offer_data['departure_city'],
                    defaults={
                        'price': offer_data['price'],
                        'duration': offer_data['duration'],
                        'meal_plan': offer_data['meal_plan'],
                        'has_wifi': offer_data['has_wifi'],
                        'has_sunbeds': offer_data['has_sunbeds'],
                        'offer_url': offer_data['offer_url'],
                        'scrape_date': timezone.now()
                    }
                )
                
                offers_count += 1
                
            except Exception as e:
                self.logger.error(f"Błąd podczas zapisywania oferty: {e}")
        
        self.logger.info(f"Zapisano {offers_count} ofert do bazy danych")