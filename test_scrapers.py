from scraper.scrapers.travelplanet_scraper import TravelplanetScraper
from scraper.scrapers.wakacje_scraper import WakacjeScraper
import logging
import json

logging.basicConfig(level=logging.INFO)

# Testowanie TravelPlanet
tp_scraper = TravelplanetScraper()
tp_results = tp_scraper.search_offers(['Bulgaria'])
print(f'TravelPlanet: Znaleziono {len(tp_results)} ofert')

# Wyświetlenie kluczy pierwszej oferty
if tp_results:
    print("\nKlucze oferty TravelPlanet:")
    print(list(tp_results[0].keys()))
    print('\nPrzykładowe oferty TravelPlanet:')
    for i, offer in enumerate(tp_results[:3], 1):
        print(f'{i}. {offer.get("hotel_name", "Brak nazwy")} - {offer.get("price", "Brak ceny")} PLN')

# Testowanie Wakacje.pl
wk_scraper = WakacjeScraper()
wk_results = wk_scraper.search_offers(['Bulgaria'])
print(f'\nWakacje.pl: Znaleziono {len(wk_results)} ofert')

# Wyświetlenie kluczy pierwszej oferty
if wk_results:
    print("\nKlucze oferty Wakacje.pl:")
    print(list(wk_results[0].keys()))
    print('\nPrzykładowe oferty Wakacje.pl:')
    for i, offer in enumerate(wk_results[:3], 1):
        print(f'{i}. {offer.get("hotel_name", "Brak nazwy")} - {offer.get("price", "Brak ceny")} PLN')