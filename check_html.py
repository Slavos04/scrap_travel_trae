import requests
from bs4 import BeautifulSoup

def check_travelplanet():
    url = 'https://www.travelplanet.pl/wakacje/bulgaria/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    print(f"\nSprawdzanie strony {url}...")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    
    # Sprawdzanie ogólnej struktury
    print("Struktura strony TravelPlanet:")
    
    # Sprawdź, czy strona używa JavaScript do ładowania treści
    scripts = soup.select('script')
    print(f"Znaleziono {len(scripts)} skryptów JavaScript")
    
    # Sprawdź, czy są jakieś kontenery, które mogą zawierać oferty
    containers = soup.select('div[class*="container"], div[class*="wrapper"], div[class*="content"], div[class*="results"]')
    print(f"Znaleziono {len(containers)} potencjalnych kontenerów")
    for i, container in enumerate(containers[:3]):
        print(f"Kontener {i+1}: {container.name} - klasy: {container.get('class')}")
    
    # Sprawdź, czy są jakieś elementy z listą
    list_elements = soup.select('ul, ol, div[class*="list"]')
    print(f"Znaleziono {len(list_elements)} elementów listy")
    
    # Znajdź wszystkie elementy div z klasami zawierającymi słowo 'offer' lub 'product'
    elements = soup.select('div[class*="offer"], div[class*="product"], div[class*="result"], div[class*="item"], div[class*="card"]')
    print(f"Znaleziono {len(elements)} potencjalnych elementów ofert")
    
    # Wyświetl klasy pierwszych 5 elementów
    for i, elem in enumerate(elements[:5]):
        print(f"Element {i+1}: {elem.name} - klasy: {elem.get('class')}")
    
    # Sprawdź, czy są jakieś linki do ofert
    links = soup.select('a[href*="oferta"], a[href*="offer"], a[href*="hotel"], a[href*="wycieczka"]')
    print(f"Znaleziono {len(links)} linków do potencjalnych ofert")
    for i, link in enumerate(links[:3]):
        print(f"Link {i+1}: {link.get('href')}")
        
    # Sprawdź, czy strona zawiera jakiekolwiek elementy z ceną
    price_elements = soup.select('[class*="price"], [class*="cena"], [class*="cost"]')
    print(f"Znaleziono {len(price_elements)} elementów z ceną")
    for i, price in enumerate(price_elements[:3]):
        print(f"Cena {i+1}: {price.text.strip()}")
        
    # Sprawdź, czy są jakieś elementy z nazwą hotelu
    hotel_elements = soup.select('[class*="hotel"], [class*="name"], h1, h2, h3, h4, h5')
    print(f"Znaleziono {len(hotel_elements)} elementów z potencjalną nazwą hotelu")
    for i, hotel in enumerate(hotel_elements[:3]):
        print(f"Hotel {i+1}: {hotel.text.strip()}")

def check_wakacje():
    url = 'https://www.wakacje.pl/wczasy/bulgaria/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    print(f"\nSprawdzanie strony {url}...")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    
    # Sprawdzanie ogólnej struktury
    print("Struktura strony Wakacje.pl:")
    
    # Sprawdź, czy strona używa JavaScript do ładowania treści
    scripts = soup.select('script')
    print(f"Znaleziono {len(scripts)} skryptów JavaScript")
    
    # Sprawdź, czy są jakieś kontenery, które mogą zawierać oferty
    containers = soup.select('div[class*="container"], div[class*="wrapper"], div[class*="content"], div[class*="results"]')
    print(f"Znaleziono {len(containers)} potencjalnych kontenerów")
    for i, container in enumerate(containers[:3]):
        print(f"Kontener {i+1}: {container.name} - klasy: {container.get('class')}")
    
    # Sprawdź, czy są jakieś elementy z listą
    list_elements = soup.select('ul, ol, div[class*="list"]')
    print(f"Znaleziono {len(list_elements)} elementów listy")
    
    # Sprawdź, czy są jakieś linki do ofert
    links = soup.select('a[href*="oferta"], a[href*="offer"], a[href*="hotel"], a[href*="wycieczka"]')
    print(f"Znaleziono {len(links)} linków do potencjalnych ofert")
    for i, link in enumerate(links[:3]):
        print(f"Link {i+1}: {link.get('href')}")
        
    # Sprawdź, czy strona zawiera jakiekolwiek elementy z ceną
    price_elements = soup.select('[class*="price"], [class*="cena"], [class*="cost"]')
    print(f"Znaleziono {len(price_elements)} elementów z ceną")
    for i, price in enumerate(price_elements[:3]):
        print(f"Cena {i+1}: {price.text.strip()}")
        
    # Sprawdź, czy są jakieś elementy z nazwą hotelu
    hotel_elements = soup.select('[class*="hotel"], [class*="name"], h1, h2, h3, h4, h5')
    print(f"Znaleziono {len(hotel_elements)} elementów z potencjalną nazwą hotelu")
    for i, hotel in enumerate(hotel_elements[:3]):
        print(f"Hotel {i+1}: {hotel.text.strip()}")

if __name__ == "__main__":
    check_travelplanet()
    check_wakacje()