from django.core.management.base import BaseCommand
from scraper.models import Destination, TravelAgency

class Command(BaseCommand):
    help = 'Initialize database with basic data (destinations and travel agencies)'

    def handle(self, *args, **options):
        # Create destinations
        destinations = [
            {'name': 'Słoneczny Brzeg', 'country': 'Bułgaria'},
            {'name': 'Złote Piaski', 'country': 'Bułgaria'},
            {'name': 'Sozopol', 'country': 'Bułgaria'},
            {'name': 'Hurghada', 'country': 'Egipt'},
            {'name': 'Sharm El Sheikh', 'country': 'Egipt'},
            {'name': 'Marsa Alam', 'country': 'Egipt'},
            {'name': 'Antalya', 'country': 'Turcja'},
            {'name': 'Bodrum', 'country': 'Turcja'},
            {'name': 'Alanya', 'country': 'Turcja'},
        ]

        for dest_data in destinations:
            Destination.objects.get_or_create(
                name=dest_data['name'],
                country=dest_data['country']
            )
            self.stdout.write(self.style.SUCCESS(f'Created destination: {dest_data["name"]}, {dest_data["country"]}'))

        # Create travel agencies
        agencies = [
            {'name': 'TravelPlanet', 'website': 'https://www.travelplanet.pl'},
            {'name': 'Wakacje.pl', 'website': 'https://www.wakacje.pl'},
            {'name': 'Fly.pl', 'website': 'https://www.fly.pl'},
        ]

        for agency_data in agencies:
            TravelAgency.objects.get_or_create(
                name=agency_data['name'],
                website=agency_data['website']
            )
            self.stdout.write(self.style.SUCCESS(f'Created agency: {agency_data["name"]}'))

        self.stdout.write(self.style.SUCCESS('Successfully initialized database with basic data'))