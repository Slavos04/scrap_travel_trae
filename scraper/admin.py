from django.contrib import admin
from .models import Destination, TravelAgency, TravelOffer


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    search_fields = ('name', 'country')
    ordering = ('country', 'name')


@admin.register(TravelAgency)
class TravelAgencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'website')
    search_fields = ('name',)


@admin.register(TravelOffer)
class TravelOfferAdmin(admin.ModelAdmin):
    list_display = ('hotel_name', 'destination', 'agency', 'price', 'departure_date', 
                   'return_date', 'duration', 'meal_plan', 'has_wifi', 'has_sunbeds')
    list_filter = ('destination__country', 'agency', 'departure_date', 'duration', 
                  'meal_plan', 'has_wifi', 'has_sunbeds')
    search_fields = ('hotel_name', 'destination__name', 'destination__country')
    date_hierarchy = 'departure_date'
    ordering = ('-scrape_date', 'price')
