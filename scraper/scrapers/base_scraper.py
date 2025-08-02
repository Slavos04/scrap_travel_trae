import requests
from bs4 import BeautifulSoup
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseScraper(ABC):
    """Bazowa klasa dla wszystkich scraperów"""
    
    def __init__(self, agency_name, agency_url):
        self.agency_name = agency_name
        self.agency_url = agency_url
        self.logger = logging.getLogger(f'scraper.{agency_name}')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        }
    
    def get_page(self, url, params=None):
        """Pobiera stronę i zwraca obiekt BeautifulSoup"""
        try:
            # Dodajemy dodatkowe nagłówki, które mogą pomóc w uniknięciu blokowania
            headers = self.headers.copy()
            headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0',
                'Upgrade-Insecure-Requests': '1',
                'Referer': url,
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7'
            })
            
            # Używamy sesji, aby obsłużyć przekierowania
            session = requests.Session()
            response = session.get(url, headers=headers, params=params, timeout=30, allow_redirects=True)
            
            # Logujemy informacje o przekierowaniach
            if response.history:
                redirect_chain = ' -> '.join([r.url for r in response.history] + [response.url])
                self.logger.info(f"Przekierowania: {redirect_chain}")
            
            response.raise_for_status()
            self.logger.info(f"Pobrano stronę {response.url} (status: {response.status_code})")
            
            # Sprawdzamy, czy strona zawiera treść HTML
            if 'text/html' not in response.headers.get('Content-Type', ''):
                self.logger.warning(f"Odpowiedź nie jest typu HTML: {response.headers.get('Content-Type')}")
            
            # Ustawiamy kodowanie na UTF-8, aby obsłużyć polskie znaki
            response.encoding = 'utf-8'
            
            return BeautifulSoup(response.text, 'lxml')
        except requests.RequestException as e:
            self.logger.error(f"Błąd podczas pobierania strony {url}: {e}")
            return None
    
    def get_min_date_str(self):
        """Zwraca minimalną datę wylotu w formacie odpowiednim dla danego scrapera"""
        min_date = datetime(2026, 5, 15)  # 15.05.2026
        return min_date.strftime('%Y-%m-%d')
    
    @abstractmethod
    def search_offers(self, countries, departure_city, min_date, duration_range, meal_plan, amenities):
        """Metoda do wyszukiwania ofert - musi być zaimplementowana przez podklasy"""
        pass
    
    @abstractmethod
    def parse_offers(self, soup, country):
        """Metoda do parsowania ofert - musi być zaimplementowana przez podklasy"""
        pass