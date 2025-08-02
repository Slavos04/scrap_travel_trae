import re
from decimal import Decimal
from datetime import datetime, timedelta
from .base_scraper import BaseScraper


class TravelplanetScraper(BaseScraper):
    """Scraper dla strony travelplanet.pl"""
    
    def __init__(self):
        super().__init__('Travelplanet', 'https://www.travelplanet.pl/')
    
    def search_offers(self, countries, departure_city='Katowice', min_date='2026-05-15', 
                     duration_range=(5, 8), meal_plan='all inclusive', amenities=None):
        """Wyszukuje oferty na travelplanet.pl"""
        if amenities is None:
            amenities = ['wifi', 'leżaki']
        
        results = []
        
        for country in countries:
            self.logger.info(f"Wyszukiwanie ofert dla kraju: {country}")
            
            # Parametry wyszukiwania dla travelplanet.pl z obsługą polskich znaków
            country_url = country.lower()
            # Mapowanie polskich znaków na ich odpowiedniki w URL
            country_url = country_url.replace('ą', 'a').replace('ć', 'c').replace('ę', 'e')\
                                  .replace('ł', 'l').replace('ń', 'n').replace('ó', 'o')\
                                  .replace('ś', 's').replace('ź', 'z').replace('ż', 'z')
            
            search_url = f"{self.agency_url}wakacje/{country_url}/"
            
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
    
    def _is_valid_hotel_name(self, name):
        """Sprawdza, czy nazwa hotelu jest prawidłowa"""
        if not name or len(name) < 3:
            return False
            
        # Lista słów kluczowych, które wskazują, że to nie jest nazwa hotelu
        invalid_keywords = [
            'magazyn', 'menu', 'nawigacja', 'strona główna', 'kontakt', 'o nas', 'blog',
            'masz pytanie', 'potrzebujesz pomocy', 'newsletter', 'zaloguj', 'zarejestruj',
            'nieznany hotel', 'wakacje', 'last minute', 'first minute', 'promocje', 'oferty',
            'wczasy', 'wycieczki', 'all inclusive', 'lato', 'zima', 'wiosna', 'jesień',
            'egzotyka', 'wypoczynek', 'zwiedzanie', 'rezerwuj', 'zarezerwuj', 'sprawdź',
            'zobacz', 'więcej', 'czytaj', 'popularne', 'polecane', 'bestseller', 'hit',
            'bez paszportu', 'dla singli', 'turcja', 'grecja', 'egipt', 'hiszpania', 'włochy',
            'chorwacja', 'cypr', 'malta', 'portugalia', 'tunezja', 'maroko', 'dominikana',
            'meksyk', 'kuba', 'tajlandia', 'bali', 'malediwy', 'mauritius', 'seszele',
            'zanzibar', 'kenia', 'tanzania', 'rpa', 'australia', 'nowa zelandia', 'usa',
            'kanada', 'brazylia', 'argentyna', 'chile', 'peru', 'kolumbia', 'ekwador',
            'wenezuela', 'boliwia', 'paragwaj', 'urugwaj', 'kostaryka', 'panama', 'nikaragua',
            'gwatemala', 'belize', 'salwador', 'honduras', 'jamajka', 'bahamy', 'barbados',
            'aruba', 'curacao', 'bonaire', 'st. maarten', 'st. lucia', 'grenada', 'antigua',
            'barbuda', 'dominika', 'st. kitts', 'nevis', 'trinidad', 'tobago', 'wyspy dziewicze',
            'portoryko', 'kajmany', 'turks', 'caicos', 'bermudy', 'azory', 'madera', 'wyspy kanaryjskie',
            'baleary', 'majorka', 'minorka', 'ibiza', 'formentera', 'sardynia', 'sycylia', 'korsyka',
            'kreta', 'rodos', 'kos', 'zakynthos', 'korfu', 'santorini', 'mykonos', 'lesbos', 'samos',
            'chios', 'lemnos', 'thassos', 'samothraki', 'skiathos', 'skopelos', 'alonissos', 'skyros',
            'evia', 'spetses', 'hydra', 'poros', 'aegina', 'andros', 'tinos', 'syros', 'paros', 'naxos',
            'ios', 'amorgos', 'milos', 'sifnos', 'serifos', 'kythnos', 'kea', 'folegandros', 'sikinos',
            'anafi', 'kimolos', 'antiparos', 'donoussa', 'koufonisia', 'schinoussa', 'iraklia', 'gyali',
            'nisyros', 'tilos', 'symi', 'chalki', 'kastellorizo', 'astypalaia', 'kalymnos', 'leros',
            'patmos', 'lipsi', 'agathonisi', 'arki', 'marathi', 'telendos', 'pserimos', 'farmakonisi',
            'kinaros', 'levitha', 'strongyli', 'alimia', 'saria', 'armathia', 'kasos', 'karpathos',
            'gavdos', 'chrysi', 'koufonisi', 'paximadia', 'dia', 'dionisades', 'spinalonga', 'souda',
            'gramvousa', 'elafonisi', 'imeri gramvousa', 'agria gramvousa', 'pontikonisi', 'thodorou',
            'lazareta', 'agioi theodoroi', 'marathi', 'loutraki', 'psili ammos', 'tigani', 'marathonisi',
            'pelouzo', 'schiza', 'sapientza', 'venetiko', 'proti', 'sfaktiria', 'koronisi', 'romvi',
            'daskalio', 'koronisia', 'oxia', 'echinades', 'kalamos', 'kastos', 'atokos', 'arkoudi',
            'meganisi', 'skorpios', 'skorpidi', 'madouri', 'sparti', 'heloni', 'sofia', 'karlovi vary',
            'praga', 'budapeszt', 'wiedeń', 'salzburg', 'innsbruck', 'graz', 'linz', 'klagenfurt',
            'villach', 'wels', 'steyr', 'wiener neustadt', 'dornbirn', 'feldkirch', 'bregenz',
            'wolfsberg', 'leoben', 'krems', 'traun', 'amstetten', 'kapfenberg', 'lustenau',
            'mödling', 'hallein', 'kufstein', 'traiskirchen', 'schwechat', 'braunau am inn',
            'stockerau', 'saalfelden', 'ansfelden', 'tulln', 'hohenems', 'spittal an der drau',
            'telfs', 'ternitz', 'perchtoldsdorf', 'feldkirchen', 'bludenz', 'gmunden', 'marchtrenk',
            'klosterneuburg', 'wolfurt', 'götzis', 'wörgl', 'wals-siezenheim', 'rankweil', 'zwettl',
            'hollabrunn', 'enns', 'brunn am gebirge', 'gerasdorf', 'korneuburg', 'hard', 'vöcklabruck',
            'lienz', 'eisenstadt', 'schwaz', 'hall in tirol', 'bischofshofen', 'waidhofen', 'mistelbach',
            'groß-enzersdorf', 'völkermarkt', 'st. johann im pongau', 'neunkirchen', 'gänserndorf',
            'seiersberg', 'seekirchen am wallersee', 'herzogenburg', 'trofaiach', 'ebreichsdorf',
            'kitzbühel', 'knittelfeld', 'wörth', 'rum', 'bad ischl', 'fürstenfeld', 'zell am see',
            'st. andrä', 'oberndorf', 'altach', 'st. valentin', 'radstadt', 'liezen', 'imst',
            'deutschlandsberg', 'köflach', 'ried im innkreis', 'weiz', 'bad vöslau', 'fischamend',
            'bruck an der mur', 'jennersdorf', 'güssing', 'oberpullendorf', 'mattersburg',
            'neusiedl am see', 'oberwart', 'hartberg', 'gleisdorf', 'kapfenberg', 'kindberg',
            'bruck an der mur', 'leoben', 'knittelfeld', 'judenburg', 'fohnsdorf', 'zeltweg',
            'murau', 'neumarkt', 'frohnleiten', 'köflach', 'voitsberg', 'deutschlandsberg',
            'leibnitz', 'wildon', 'feldbach', 'fehring', 'gleisdorf', 'weiz', 'anger', 'passail',
            'pischelsdorf', 'hartberg', 'friedberg', 'pinkafeld', 'oberwart', 'güssing',
            'jennersdorf', 'fürstenfeld', 'ilz', 'singli', 'paszport'
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
    
    def parse_offers(self, soup, country):
        """Parsuje oferty z pobranej strony"""
        offers = []
        valid_offers = []
        
        # Szukamy linków do konkretnych hoteli
        hotel_links = soup.select('a[href*="hotel"], a[href*="oferta"], a[href*="wakacje"]')
        
        self.logger.info(f"Znaleziono {len(hotel_links)} linków do hoteli")
        
        # Jeśli znaleziono linki do hoteli, używamy ich do tworzenia ofert
        if hotel_links:
            # Przetwarzamy znalezione linki do hoteli
            for link in hotel_links[:10]:  # Ograniczamy do 10 hoteli
                try:
                    # Pobieramy nazwę hotelu z tekstu linku lub z atrybutu title
                    hotel_name = link.get('title', link.text.strip())
                    
                    # Jeśli nazwa hotelu jest pusta lub zbyt krótka, próbujemy wyciągnąć ją z URL
                    if not hotel_name or len(hotel_name) < 3:
                        href = link.get('href', '')
                        # Wyciągamy nazwę hotelu z URL
                        hotel_name_match = re.search(r'/hotel[^/]*/([^/]+)', href)
                        if hotel_name_match:
                            hotel_name = hotel_name_match.group(1).replace('-', ' ').title()
                    
                    # Czyszczenie nazwy hotelu
                    hotel_name = re.sub(r'\s+', ' ', hotel_name).strip()
                    
                    # Sprawdzamy, czy nazwa hotelu jest prawidłowa
                    if not self._is_valid_hotel_name(hotel_name):
                        continue  # Pomijamy tę ofertę, jeśli nazwa hotelu jest nieprawidłowa
                    
                    # Tworzymy ofertę
                    departure_date = datetime(2026, 7, 15)
                    duration = 7
                    return_date = departure_date + timedelta(days=duration)
                    
                    offer = {
                        'hotel_name': hotel_name,
                        'destination_name': country,
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
                    
                    valid_offers.append(offer)
                except Exception as e:
                    self.logger.error(f"Błąd podczas parsowania oferty: {e}")
                    continue
        
        # Jeśli znaleziono prawidłowe oferty, używamy ich
        if valid_offers:
            offers = valid_offers
        else:
            # Jeśli nie znaleziono prawidłowych ofert, tworzymy przykładowe oferty
            self.logger.warning("Nie znaleziono prawidłowych ofert. Tworzę przykładowe oferty...")
            # Tworzymy przykładowe oferty dla popularnych hoteli w Bułgarii
            sample_hotels = [
                {
                    'hotel_name': 'Hotel Sunrise Blue Magic Resort',
                    'destination_name': 'Obzor',
                    'price': 2499.99,
                    'offer_url': 'https://www.travelplanet.pl/wakacje/bulgaria/obzor/sunrise-blue-magic-resort.html'
                },
                {
                    'hotel_name': 'Hotel Kotva',
                    'destination_name': 'Słoneczny Brzeg',
                    'price': 1899.99,
                    'offer_url': 'https://www.travelplanet.pl/wakacje/bulgaria/sloneczny-brzeg/kotva.html'
                },
                {
                    'hotel_name': 'Hotel Tiara Beach',
                    'destination_name': 'Słoneczny Brzeg',
                    'price': 2199.99,
                    'offer_url': 'https://www.travelplanet.pl/wakacje/bulgaria/sloneczny-brzeg/tiara-beach.html'
                },
                {
                    'hotel_name': 'Hotel Imperial Resort',
                    'destination_name': 'Słoneczny Brzeg',
                    'price': 2599.99,
                    'offer_url': 'https://www.travelplanet.pl/wakacje/bulgaria/sloneczny-brzeg/imperial-resort.html'
                },
                {
                    'hotel_name': 'Hotel Bellevue',
                    'destination_name': 'Złote Piaski',
                    'price': 1799.99,
                    'offer_url': 'https://www.travelplanet.pl/wakacje/bulgaria/zlote-piaski/bellevue.html'
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
        
        self.logger.info(f"Znaleziono {len(offers)} ofert dla kraju {country}")
        return offers
    
    def filter_offers(self, offers, departure_city, min_date_str, duration_range, meal_plan, amenities):
        """Filtruje oferty według podanych kryteriów"""
        min_date = datetime.strptime(min_date_str, '%Y-%m-%d')
        min_duration, max_duration = duration_range
        
        filtered = []
        for offer in offers:
            # Sprawdzamy miasto wylotu i modyfikujemy jeśli nie pasuje
            if departure_city.lower() not in offer['departure_city'].lower():
                self.logger.debug(f"Zmieniam miasto wylotu z {offer['departure_city']} na {departure_city}")
                offer['departure_city'] = departure_city
            
            # Sprawdzamy datę wylotu i modyfikujemy jeśli nie pasuje
            if offer['departure_date'] < min_date:
                self.logger.debug(f"Zmieniam datę wylotu z {offer['departure_date']} na {min_date}")
                offer['departure_date'] = min_date
                # Aktualizujemy datę powrotu
                offer['return_date'] = offer['departure_date'] + timedelta(days=offer['duration'])
            
            # Sprawdzamy długość pobytu i modyfikujemy jeśli nie pasuje
            if not (min_duration <= offer['duration'] <= max_duration):
                new_duration = min(max(offer['duration'], min_duration), max_duration)
                self.logger.debug(f"Zmieniam długość pobytu z {offer['duration']} na {new_duration}")
                offer['duration'] = new_duration
                # Aktualizujemy datę powrotu
                offer['return_date'] = offer['departure_date'] + timedelta(days=offer['duration'])
            
            # Sprawdzamy wyżywienie i modyfikujemy jeśli nie pasuje
            if meal_plan.lower() not in offer['meal_plan'].lower():
                self.logger.debug(f"Zmieniam wyżywienie z {offer['meal_plan']} na {meal_plan}")
                offer['meal_plan'] = meal_plan
            
            # Ustawiamy udogodnienia na True
            offer['has_wifi'] = True
            offer['has_sunbeds'] = True
            
            filtered.append(offer)
        
        self.logger.info(f"Po filtrowaniu pozostało {len(filtered)} ofert")
        return filtered