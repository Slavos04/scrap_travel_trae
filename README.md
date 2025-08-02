# Travel Scraper

Aplikacja do monitorowania cen ofert turystycznych do Bułgarii, Egiptu i Turcji na stronach:
- travelplanet.pl
- wakacje.pl
- fly.pl

## Wymagania

- Python 3.8+
- Django 5.0.1
- Pozostałe zależności w pliku requirements.txt

## Instalacja

1. Sklonuj repozytorium
2. Utwórz wirtualne środowisko: `python -m venv venv`
3. Aktywuj wirtualne środowisko:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Uruchom skrypt instalacyjny: `python run.py`

Skrypt automatycznie:
- Zainstaluje wymagane zależności
- Wykona migracje bazy danych
- Zainicjalizuje podstawowe dane (destynacje i biura podróży)
- Utworzy konto administratora (jeśli nie istnieje)
- Uruchomi serwer deweloperski

Alternatywnie, możesz wykonać te kroki ręcznie:
1. Zainstaluj zależności: `pip install -r requirements.txt`
2. Wykonaj migracje: `python manage.py migrate`
3. Zainicjalizuj dane: `python manage.py initialize_data`
4. Uruchom serwer: `python manage.py runserver`

## Funkcjonalności

- Codzienne sprawdzanie cen ofert turystycznych
- Parametry wyszukiwania:
  - Destynacje: Bułgaria, Egipt, Turcja
  - Wylot z Katowic
  - Data wylotu od 15.05.2026
  - Czas pobytu: 5-8 dni
  - Wyżywienie: All Inclusive
  - Darmowe WiFi i leżaki
- Zapisywanie wyników do bazy danych
- Interfejs webowy do przeglądania wyników
- Możliwość ręcznego uruchomienia scrapera z własnymi parametrami

## Korzystanie z aplikacji

### Interfejs użytkownika

Po uruchomieniu serwera, interfejs użytkownika jest dostępny pod adresem: http://127.0.0.1:8000/

Dostępne funkcje:
- Strona główna: statystyki i najnowsze/najtańsze oferty
- Lista ofert: przeglądanie i filtrowanie wszystkich ofert
- Szczegóły oferty: pełne informacje o wybranej ofercie
- Ręczne scrapowanie: uruchomienie scrapera z własnymi parametrami

### Panel administracyjny

Panel administracyjny dostępny jest pod adresem: http://127.0.0.1:8000/admin/

W panelu można:
- Zarządzać destynacjami
- Zarządzać biurami podróży
- Przeglądać i edytować oferty turystyczne
- Zarządzać zadaniami harmonogramu