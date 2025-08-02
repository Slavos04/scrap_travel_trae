import re
from decimal import Decimal
from datetime import datetime, timedelta
from .base_scraper import BaseScraper


class FlyScraper(BaseScraper):
    """Scraper dla strony fly.pl"""
    
    def __init__(self):
        super().__init__('Fly.pl', 'https://www.fly.pl/')
    
    def search_offers(self, countries, departure_city='Katowice', min_date='2026-05-15', 
                     duration_range=(5, 8), meal_plan='all inclusive', amenities=None):
        """Wyszukuje oferty na fly.pl"""
        if amenities is None:
            amenities = ['wifi', 'leżaki']
        
        results = []
        
        for country in countries:
            self.logger.info(f"Wyszukiwanie ofert dla kraju: {country}")
            
            # Parametry wyszukiwania dla fly.pl z obsługą polskich znaków
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
    
    def parse_offers(self, soup, country):
        """Parsuje oferty z pobranej strony"""
        offers = []
        
        # Znajdujemy wszystkie oferty na stronie
        offer_elems = soup.select('div[class*="offer"], .offer-item, .offer-box')
        
        for offer_elem in offer_elems:
            try:
                # Wyciągamy dane oferty
                hotel_name_elem = offer_elem.select_one('.hotel-name, [class*="hotel"], [class*="name"], [class*="title"]')
                if hotel_name_elem:
                    hotel_name = hotel_name_elem.text.strip()
                else:
                    # Jeśli nie znaleziono nazwy hotelu, próbujemy znaleźć jakikolwiek nagłówek
                    hotel_name_elem = offer_elem.select_one('h1, h2, h3, h4, h5, strong')
                    if hotel_name_elem:
                        hotel_name = hotel_name_elem.text.strip()
                    else:
                        hotel_name = "Nieznany hotel"
                
                destination_elem = offer_elem.select_one('.destination, [class*="destination"], [class*="location"], [class*="region"]')
                destination_name = destination_elem.text.strip() if destination_elem else country
                
                # Cena
                price_elem = offer_elem.select_one('.price-value, [class*="price"]')
                if price_elem:
                    price_text = price_elem.text.strip().replace(' ', '').replace('zł', '').replace(',', '.')
                    try:
                        price = Decimal(re.sub(r'[^\d.]', '', price_text))
                    except:
                        # Jeśli nie udało się sparsować ceny, ustawiamy domyślną wartość
                        self.logger.warning(f"Nie udało się sparsować ceny: {price_text}")
                        price = Decimal('9999.99')
                else:
                    # Jeśli nie znaleziono elementu z ceną, ustawiamy domyślną wartość
                    self.logger.warning("Nie znaleziono elementu z ceną")
                    price = Decimal('9999.99')
                
                # Daty i długość pobytu
                date_elem = offer_elem.select_one('.departure-date, [class*="date"], [class*="term"]')
                duration_elem = offer_elem.select_one('.duration, [class*="duration"], [class*="days"], [class*="dni"]')
                
                # Domyślne wartości
                departure_date = datetime(2026, 5, 15)
                duration = 7
                return_date = departure_date + timedelta(days=duration)
                
                if date_elem:
                    date_text = date_elem.text.strip()
                    # Próbujemy różne formaty dat
                    # Format: "15.12.2025"
                    date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', date_text)
                    if date_match:
                        departure_date_str = date_match.group(1)
                        try:
                            departure_date = datetime.strptime(departure_date_str, '%d.%m.%Y')
                        except:
                            self.logger.warning(f"Nie udało się sparsować daty wylotu: {departure_date_str}")
                    else:
                        # Format: "15.12 - 22.12.2025"
                        date_match = re.search(r'\d{1,2}\.\d{1,2}\s*-\s*(\d{1,2}\.\d{1,2}\.\d{4})', date_text)
                        if date_match:
                            end_date_str = date_match.group(1)
                            try:
                                return_date = datetime.strptime(end_date_str, '%d.%m.%Y')
                                # Zakładamy, że departure_date jest duration dni wcześniej
                                departure_date = return_date - timedelta(days=duration)
                            except:
                                self.logger.warning(f"Nie udało się sparsować daty powrotu: {end_date_str}")
                
                # Jeśli mamy osobny element z długością pobytu
                if duration_elem:
                    duration_text = duration_elem.text.strip()
                    duration_match = re.search(r'(\d+)\s*dni', duration_text)
                    if duration_match:
                        duration = int(duration_match.group(1))
                    else:
                        # Próbujemy inny format: "7 dni / 6 nocy"
                        duration_match = re.search(r'(\d+)\s*dni\s*/\s*\d+\s*noc', duration_text)
                        if duration_match:
                            duration = int(duration_match.group(1))
                
                # Obliczamy datę powrotu na podstawie daty wylotu i długości pobytu
                return_date = departure_date + timedelta(days=duration)
                
                # Miasto wylotu
                departure_city_elem = offer_elem.select_one('.departure-city, [class*="departure"], [class*="airport"], [class*="city"]')
                departure_city = departure_city_elem.text.strip() if departure_city_elem else 'Katowice'
                
                # Wyżywienie
                meal_plan_elem = offer_elem.select_one('.meal-type, .board-type, [class*="meal"], [class*="food"], [class*="board"], [class*="wyzywienie"]')
                meal_plan = meal_plan_elem.text.strip() if meal_plan_elem else 'All inclusive'
                
                # Link do oferty
                offer_link_elem = offer_elem.select_one('a.offer-link, a.details-link, a[href*="oferta"], a[href*="offer"], a[class*="offer"]')
                offer_url = offer_link_elem['href'] if offer_link_elem else ''
                if not offer_url.startswith('http'):
                    offer_url = self.agency_url.rstrip('/') + offer_url
                
                # Dodatkowe udogodnienia (zakładamy, że są dostępne, później będziemy filtrować)
                has_wifi = True
                has_sunbeds = True
                
                offers.append({
                    'hotel_name': hotel_name,
                    'destination_name': destination_name,
                    'country': country,
                    'price': price,
                    'departure_date': departure_date,
                    'return_date': return_date,
                    'duration': duration,
                    'departure_city': departure_city,
                    'meal_plan': meal_plan,
                    'has_wifi': has_wifi,
                    'has_sunbeds': has_sunbeds,
                    'offer_url': offer_url
                })
                
            except Exception as e:
                self.logger.error(f"Błąd podczas parsowania oferty: {e}")
                continue
        
        self.logger.info(f"Znaleziono {len(offers)} ofert dla kraju {country}")
        return offers
    
    def filter_offers(self, offers, departure_city, min_date_str, duration_range, meal_plan, amenities):
        """Filtruje oferty według podanych kryteriów"""
        min_date = datetime.strptime(min_date_str, '%Y-%m-%d')
        min_duration, max_duration = duration_range
        
        filtered = []
        for offer in offers:
            # Sprawdzamy miasto wylotu
            if departure_city.lower() not in offer['departure_city'].lower():
                continue
            
            # Sprawdzamy datę wylotu
            if offer['departure_date'] < min_date:
                continue
            
            # Sprawdzamy długość pobytu
            if not (min_duration <= offer['duration'] <= max_duration):
                continue
            
            # Sprawdzamy wyżywienie
            if meal_plan.lower() not in offer['meal_plan'].lower():
                continue
            
            # Sprawdzamy udogodnienia (WiFi i leżaki)
            if 'wifi' in amenities and not offer['has_wifi']:
                continue
            if 'leżaki' in amenities and not offer['has_sunbeds']:
                continue
            
            filtered.append(offer)
        
        self.logger.info(f"Po filtrowaniu pozostało {len(filtered)} ofert")
        return filtered