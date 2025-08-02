from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import FormView
from django.contrib import messages
from django.db.models import Min
from django.utils import timezone
from django.http import HttpResponse
from django import forms

from .models import Destination, TravelAgency, TravelOffer
from .tasks import scrape_travel_offers


class HomeView(TemplateView):
    """Widok strony głównej"""
    template_name = 'scraper/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Pobieramy statystyki
        context['total_offers'] = TravelOffer.objects.count()
        context['destinations_count'] = Destination.objects.count()
        context['agencies_count'] = TravelAgency.objects.count()
        
        # Pobieramy najnowsze oferty
        context['latest_offers'] = TravelOffer.objects.order_by('-scrape_date')[:10]
        
        # Pobieramy najtańsze oferty
        context['cheapest_offers'] = TravelOffer.objects.order_by('price')[:10]
        
        # Pobieramy ostatnią datę scrapowania
        last_scrape = TravelOffer.objects.order_by('-scrape_date').first()
        context['last_scrape_date'] = last_scrape.scrape_date if last_scrape else None
        
        return context


class OfferListView(ListView):
    """Widok listy ofert"""
    model = TravelOffer
    template_name = 'scraper/offer_list.html'
    context_object_name = 'offers'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrowanie po kraju
        country = self.request.GET.get('country')
        if country:
            queryset = queryset.filter(destination__country=country)
        
        # Filtrowanie po biurze podróży
        agency = self.request.GET.get('agency')
        if agency:
            queryset = queryset.filter(agency__name=agency)
        
        # Filtrowanie po cenie
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filtrowanie po dacie wylotu
        min_date = self.request.GET.get('min_date')
        if min_date:
            queryset = queryset.filter(departure_date__gte=min_date)
        
        # Filtrowanie po długości pobytu
        duration = self.request.GET.get('duration')
        if duration:
            queryset = queryset.filter(duration=duration)
        
        # Filtrowanie po wyżywieniu
        meal_plan = self.request.GET.get('meal_plan')
        if meal_plan:
            queryset = queryset.filter(meal_plan__icontains=meal_plan)
        
        # Filtrowanie po udogodnieniach
        if self.request.GET.get('wifi'):
            queryset = queryset.filter(has_wifi=True)
        if self.request.GET.get('sunbeds'):
            queryset = queryset.filter(has_sunbeds=True)
        
        # Sortowanie
        sort = self.request.GET.get('sort', '-scrape_date')
        queryset = queryset.order_by(sort)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dodajemy listy krajów i biur podróży do kontekstu
        context['countries'] = Destination.objects.values_list('country', flat=True).distinct()
        context['agencies'] = TravelAgency.objects.all()
        
        # Dodajemy parametry filtrowania do kontekstu
        context['filters'] = self.request.GET.dict()
        
        return context


class OfferDetailView(DetailView):
    """Widok szczegółów oferty"""
    model = TravelOffer
    template_name = 'scraper/offer_detail.html'
    context_object_name = 'offer'


class ManualScrapeForm(forms.Form):
    """Formularz do ręcznego uruchamiania scrapera"""
    countries = forms.MultipleChoiceField(
        choices=[(c, c) for c in ['Bułgaria', 'Egipt', 'Turcja']],
        initial=['Bułgaria', 'Egipt', 'Turcja'],
        required=True,
        widget=forms.CheckboxSelectMultiple,
        label='Kraje'
    )
    departure_city = forms.CharField(
        initial='Katowice',
        required=True,
        label='Miasto wylotu'
    )
    min_date = forms.DateField(
        initial='2026-05-15',
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Minimalna data wylotu'
    )
    min_duration = forms.IntegerField(
        initial=5,
        required=True,
        min_value=1,
        max_value=30,
        label='Minimalna długość pobytu (dni)'
    )
    max_duration = forms.IntegerField(
        initial=8,
        required=True,
        min_value=1,
        max_value=30,
        label='Maksymalna długość pobytu (dni)'
    )
    meal_plan = forms.CharField(
        initial='all inclusive',
        required=True,
        label='Wyżywienie'
    )
    wifi = forms.BooleanField(
        initial=True,
        required=False,
        label='Darmowe WiFi'
    )
    sunbeds = forms.BooleanField(
        initial=True,
        required=False,
        label='Darmowe leżaki'
    )


class ManualScrapeView(FormView):
    """Widok do ręcznego uruchamiania scrapera"""
    template_name = 'scraper/manual_scrape.html'
    form_class = ManualScrapeForm
    success_url = '/scraper/offers/'
    
    def form_valid(self, form):
        # Pobieramy dane z formularza
        countries = form.cleaned_data['countries']
        departure_city = form.cleaned_data['departure_city']
        min_date = form.cleaned_data['min_date'].strftime('%Y-%m-%d')
        duration_range = (form.cleaned_data['min_duration'], form.cleaned_data['max_duration'])
        meal_plan = form.cleaned_data['meal_plan']
        amenities = []
        if form.cleaned_data['wifi']:
            amenities.append('wifi')
        if form.cleaned_data['sunbeds']:
            amenities.append('leżaki')
        
        # Uruchamiamy scrapery
        from .scrapers.scraper_manager import ScraperManager
        manager = ScraperManager()
        results = manager.run_all_scrapers(
            countries, 
            departure_city, 
            min_date, 
            duration_range, 
            meal_plan, 
            amenities
        )
        
        messages.success(self.request, f"Znaleziono {len(results)} ofert. Zapisano do bazy danych.")
        # Zmieniamy przekierowanie na 'offer_list' zamiast ścieżki URL
        return redirect('offer_list')


def run_scraper_view(request):
    """Widok do uruchamiania scrapera z poziomu interfejsu"""
    if request.method == 'POST':
        count = scrape_travel_offers()
        messages.success(request, f"Znaleziono {count} ofert. Zapisano do bazy danych.")
        return redirect('offer_list')
    return redirect('home')
