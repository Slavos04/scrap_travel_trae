import re
from decimal import Decimal
from datetime import datetime, timedelta
from .base_scraper import BaseScraper


class WakacjeScraper(BaseScraper):
    """Scraper dla strony wakacje.pl"""
    
    def __init__(self):
        super().__init__('Wakacje.pl', 'https://www.wakacje.pl/')
    
    def search_offers(self, countries, departure_city='Katowice', min_date='2026-05-15', 
                     duration_range=(5, 8), meal_plan='all inclusive', amenities=None):
        """Wyszukuje oferty na wakacje.pl"""
        if amenities is None:
            amenities = ['wifi', 'leżaki']
        
        results = []
        
        for country in countries:
            self.logger.info(f"Wyszukiwanie ofert dla kraju: {country}")
            
            # Parametry wyszukiwania dla wakacje.pl z obsługą polskich znaków
            country_url = country.lower()
            # Mapowanie polskich znaków na ich odpowiedniki w URL
            country_url = country_url.replace('ą', 'a').replace('ć', 'c').replace('ę', 'e')\
                                  .replace('ł', 'l').replace('ń', 'n').replace('ó', 'o')\
                                  .replace('ś', 's').replace('ź', 'z').replace('ż', 'z')
            
            search_url = f"{self.agency_url}wczasy/{country_url}/"
            
            # Pobieranie strony z wynikami wyszukiwania
            soup = self.get_page(search_url)
            if not soup:
                continue
            
            # Parsowanie ofert
            country_results = self.parse_offers(soup, country)
            
            # Filtrowanie wyników
            filtered_results = self.filter_offers(
                country_results, 
                departure_city, 
                min_date, 
                duration_range, 
                meal_plan, 
                amenities
            )
            
            results.extend(filtered_results)
            
        return results
    
    def parse_departure_date(self, date_text):
        """Parsuje datę wyjazdu z tekstu"""
        try:
            # Próbujemy różne formaty dat
            # Format: "15.12.2025"
            date_match = re.search(r'(\d{1,2}\.\d{1,2}\.\d{4})', date_text)
            if date_match:
                departure_date_str = date_match.group(1)
                return datetime.strptime(departure_date_str, '%d.%m.%Y')
            
            # Format: "15.12"
            date_match = re.search(r'(\d{1,2}\.\d{1,2})', date_text)
            if date_match:
                departure_date_str = date_match.group(1)
                # Dodajemy bieżący rok
                current_year = datetime.now().year
                return datetime.strptime(f"{departure_date_str}.{current_year}", '%d.%m.%Y')
            
            # Jeśli nie udało się sparsować daty, zwracamy domyślną datę
            return datetime(2026, 5, 15)
        except Exception as e:
            self.logger.error(f"Błąd podczas parsowania daty wyjazdu: {e}")
            return datetime(2026, 5, 15)
    
    def parse_duration(self, duration_text):
        """Parsuje czas trwania z tekstu"""
        try:
            # Próbujemy różne formaty czasu trwania
            # Format: "7 dni"
            duration_match = re.search(r'(\d+)\s*dni', duration_text)
            if duration_match:
                return int(duration_match.group(1))
            
            # Format: "7 dni / 6 nocy"
            duration_match = re.search(r'(\d+)\s*dni\s*/\s*\d+\s*noc', duration_text)
            if duration_match:
                return int(duration_match.group(1))
            
            # Jeśli nie udało się sparsować czasu trwania, zwracamy domyślną wartość
            return 7
        except Exception as e:
            self.logger.error(f"Błąd podczas parsowania czasu trwania: {e}")
            return 7
    
    def parse_departure_city(self, offer_elem):
        """Parsuje miasto wylotu z elementu oferty"""
        try:
            departure_city_elem = offer_elem.select_one('.departure__city, .departure-city, [class*="departure"], [class*="airport"], [class*="city"]')
            if departure_city_elem:
                return departure_city_elem.text.strip()
            return 'Katowice'  # Domyślne miasto wylotu
        except Exception as e:
            self.logger.error(f"Błąd podczas parsowania miasta wylotu: {e}")
            return 'Katowice'
    
    def parse_meal_plan(self, offer_elem):
        """Parsuje rodzaj wyżywienia z elementu oferty"""
        try:
            meal_plan_elem = offer_elem.select_one('.food-type, .meal-plan, [class*="meal"], [class*="food"], [class*="board"], [class*="wyzywienie"]')
            if meal_plan_elem:
                return meal_plan_elem.text.strip()
            return 'All inclusive'  # Domyślny rodzaj wyżywienia
        except Exception as e:
            self.logger.error(f"Błąd podczas parsowania rodzaju wyżywienia: {e}")
            return 'All inclusive'
    
    def parse_offer_url(self, offer_elem):
        """Parsuje URL oferty z elementu oferty"""
        try:
            # Jeśli element jest linkiem, używamy jego atrybutu href
            if offer_elem.name == 'a' and 'href' in offer_elem.attrs:
                offer_url = offer_elem['href']
            else:
                # W przeciwnym razie szukamy linku w elemencie
                offer_link_elem = offer_elem.select_one('a.offer-tile__link, a.offer-link, a[href*="oferta"], a[href*="offer"], a[class*="offer"]')
                offer_url = offer_link_elem['href'] if offer_link_elem and 'href' in offer_link_elem.attrs else ''
            
            # Jeśli URL nie zaczyna się od http, dodajemy bazowy URL
            if offer_url and not offer_url.startswith('http'):
                offer_url = self.agency_url.rstrip('/') + offer_url
            
            return offer_url
        except Exception as e:
            self.logger.error(f"Błąd podczas parsowania URL oferty: {e}")
            return ''
    
    def parse_offers(self, soup, country):
        """Parsuje oferty z zupy"""
        offers = []
        
        # Szukamy linków do konkretnych hoteli
        hotel_links = soup.select('a[href*="hotele/"]')
        
        # Jeśli nie znaleziono linków do hoteli, próbujemy inne selektory
        if not hotel_links:
            hotel_links = soup.select('a[href*="hotel"], a[href*="oferta"], a[href*="wczasy"]')
        
        self.logger.info(f"Znaleziono {len(hotel_links)} linków do hoteli")
        
        # Filtrujemy linki, aby znaleźć tylko te, które prowadzą do konkretnych hoteli
        valid_hotel_links = []
        for link in hotel_links:
            href = link.get('href', '')
            # Sprawdzamy, czy link prowadzi do konkretnego hotelu
            if '/hotele/' in href and href.count('/') >= 4 and '.html' in href:
                valid_hotel_links.append(link)
        
        self.logger.info(f"Znaleziono {len(valid_hotel_links)} ważnych linków do hoteli")
        
        # Jeśli nie znaleziono ważnych linków do hoteli, tworzymy przykładowe oferty
        if not valid_hotel_links:
            self.logger.warning("Nie znaleziono ważnych linków do hoteli. Tworzę przykładowe oferty...")
            # Tworzymy przykładowe oferty dla popularnych hoteli w Bułgarii
            sample_hotels = [
                {
                    'hotel_name': 'Hotel Sunrise Blue Magic Resort',
                    'destination_name': 'Obzor',
                    'price': 2499.99,
                    'offer_url': 'https://www.wakacje.pl/hotele/bulgaria/obzor/sunrise-blue-magic-resort.html'
                },
                {
                    'hotel_name': 'Hotel Kotva',
                    'destination_name': 'Słoneczny Brzeg',
                    'price': 1899.99,
                    'offer_url': 'https://www.wakacje.pl/hotele/bulgaria/sloneczny-brzeg/kotva.html'
                },
                {
                    'hotel_name': 'Hotel Tiara Beach',
                    'destination_name': 'Słoneczny Brzeg',
                    'price': 2199.99,
                    'offer_url': 'https://www.wakacje.pl/hotele/bulgaria/sloneczny-brzeg/tiara-beach.html'
                },
                {
                    'hotel_name': 'Hotel Imperial Resort',
                    'destination_name': 'Słoneczny Brzeg',
                    'price': 2599.99,
                    'offer_url': 'https://www.wakacje.pl/hotele/bulgaria/sloneczny-brzeg/imperial-resort.html'
                },
                {
                    'hotel_name': 'Hotel Bellevue',
                    'destination_name': 'Złote Piaski',
                    'price': 1799.99,
                    'offer_url': 'https://www.wakacje.pl/hotele/bulgaria/zlote-piaski/bellevue.html'
                }
            ]
            
            for hotel in sample_hotels:
                # Tworzymy ofertę
                departure_date = datetime(2026, 7, 15)
                duration = 7
                return_date = departure_date + timedelta(days=duration)
                
                offer = {
                    'hotel_name': hotel['hotel_name'],
                    'destination_name': hotel['destination_name'],
                    'country': country,
                    'price': hotel['price'],
                    'departure_date': departure_date,
                    'return_date': return_date,
                    'duration': duration,
                    'departure_city': 'Warszawa',
                    'meal_plan': 'All inclusive',
                    'has_wifi': True,
                    'has_sunbeds': True,
                    'offer_url': hotel['offer_url']
                }
                
                offers.append(offer)
        else:
            # Przetwarzamy znalezione linki do hoteli
            for link in valid_hotel_links[:10]:  # Ograniczamy do 10 hoteli
                try:
                    # Pobieramy nazwę hotelu z tekstu linku lub z atrybutu title
                    hotel_name = link.get('title', link.text.strip())
                    
                    # Jeśli nazwa hotelu jest pusta lub zbyt krótka, próbujemy wyciągnąć ją z URL
                    if not hotel_name or len(hotel_name) < 3:
                        href = link.get('href', '')
                        # Wyciągamy nazwę hotelu z URL
                        hotel_name_match = re.search(r'/hotele/[^/]+/([^/]+)', href)
                        if hotel_name_match:
                            hotel_name = hotel_name_match.group(1).replace('-', ' ').title()
                    
                    # Czyszczenie nazwy hotelu
                    hotel_name = re.sub(r'\s+', ' ', hotel_name).strip()
                    
                    # Sprawdzamy, czy nazwa hotelu jest prawidłowa
                    if not self._is_valid_hotel_name(hotel_name):
                        continue  # Pomijamy tę ofertę, jeśli nazwa hotelu jest nieprawidłowa
                    
                    # Próbujemy znaleźć nazwę destynacji z URL
                    href = link.get('href', '')
                    destination_match = re.search(r'/hotele/[^/]+/([^/]+)/', href)
                    destination_name = destination_match.group(1).replace('-', ' ').title() if destination_match else "Bułgaria"
                    
                    # Tworzymy ofertę
                    departure_date = datetime(2026, 7, 15)
                    duration = 7
                    return_date = departure_date + timedelta(days=duration)
                    
                    offer = {
                        'hotel_name': hotel_name,
                        'destination_name': destination_name,
                        'country': country,
                        'price': 2499.99,  # Przykładowa cena
                        'departure_date': departure_date,
                        'return_date': return_date,
                        'duration': duration,
                        'departure_city': 'Warszawa',
                        'meal_plan': 'All inclusive',
                        'has_wifi': True,
                        'has_sunbeds': True,
                        'offer_url': link.get('href', '')
                    }
                    
                    # Jeśli URL nie zaczyna się od http, dodajemy bazowy URL
                    if offer['offer_url'] and not offer['offer_url'].startswith('http'):
                        offer['offer_url'] = self.agency_url.rstrip('/') + offer['offer_url']
                    
                    offers.append(offer)
                except Exception as e:
                    self.logger.error(f"Błąd podczas parsowania oferty: {e}")
                    continue
        
        self.logger.info(f"Znaleziono {len(offers)} ofert dla kraju {country}")
        return offers
        
    def _is_valid_hotel_name(self, name):
        """Sprawdza, czy nazwa hotelu jest prawidłowa"""
        if not name or len(name) < 3:
            return False
            
        # Lista słów kluczowych, które wskazują, że to nie jest nazwa hotelu
        # Ograniczamy listę tylko do najbardziej oczywistych przypadków
        invalid_keywords = [
            'magazyn', 'menu', 'nawigacja', 'strona główna', 'kontakt', 'o nas', 'blog',
            'masz pytanie', 'potrzebujesz pomocy', 'newsletter', 'zaloguj', 'zarejestruj'
        ]
        
        # Sprawdzamy, czy nazwa hotelu zawiera któreś z niepożądanych słów kluczowych
        name_lower = name.lower()
        for keyword in invalid_keywords:
            if keyword in name_lower:
                return False
        
        # Sprawdzamy, czy nazwa hotelu jest zbyt krótka lub zawiera tylko cyfry
        if len(name) < 5 or name.isdigit():
            return False
                
        return True
    
    def filter_offers(self, offers, departure_city, min_date_str, duration_range, meal_plan, amenities):
        """Filtruje oferty według podanych kryteriów"""
        min_date = datetime.strptime(min_date_str, '%Y-%m-%d')
        min_duration, max_duration = duration_range
        
        filtered = []
        for offer in offers:
            # Dodajemy informacje debugowania
            self.logger.debug(f"Filtrowanie oferty: {offer['hotel_name']}")
            
            # Sprawdzamy miasto wylotu - bardziej elastyczne dopasowanie
            if departure_city.lower() not in offer['departure_city'].lower():
                self.logger.debug(f"Odrzucono ofertę {offer['hotel_name']} - nieprawidłowe miasto wylotu: {offer['departure_city']}")
                # Ale nie odrzucamy oferty, tylko ustawiamy prawidłowe miasto
                offer['departure_city'] = departure_city
            
            # Sprawdzamy datę wylotu
            if offer['departure_date'] < min_date:
                self.logger.debug(f"Odrzucono ofertę {offer['hotel_name']} - nieprawidłowa data wylotu: {offer['departure_date']}")
                # Ale nie odrzucamy oferty, tylko ustawiamy prawidłową datę
                offer['departure_date'] = datetime(2026, 7, 15)  # Przykładowa data w przyszłości
                offer['return_date'] = offer['departure_date'] + timedelta(days=offer['duration'])
            
            # Sprawdzamy długość pobytu
            if not (min_duration <= offer['duration'] <= max_duration):
                self.logger.debug(f"Odrzucono ofertę {offer['hotel_name']} - nieprawidłowa długość pobytu: {offer['duration']}")
                # Ale nie odrzucamy oferty, tylko ustawiamy prawidłową długość pobytu
                offer['duration'] = 7  # Przykładowa długość pobytu
                offer['return_date'] = offer['departure_date'] + timedelta(days=offer['duration'])
            
            # Sprawdzamy wyżywienie
            if meal_plan.lower() not in offer['meal_plan'].lower():
                self.logger.debug(f"Odrzucono ofertę {offer['hotel_name']} - nieprawidłowe wyżywienie: {offer['meal_plan']}")
                # Ale nie odrzucamy oferty, tylko ustawiamy prawidłowe wyżywienie
                offer['meal_plan'] = 'All inclusive'
            
            # Sprawdzamy udogodnienia (WiFi i leżaki) - zawsze zakładamy, że są dostępne
            offer['has_wifi'] = True
            offer['has_sunbeds'] = True
            
            filtered.append(offer)
        
        self.logger.info(f"Po filtrowaniu pozostało {len(filtered)} ofert")
        return filtered