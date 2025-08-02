from django.db import models
from django.utils import timezone


class Destination(models.Model):
    """Model reprezentujący destynację turystyczną"""
    name = models.CharField(max_length=100, verbose_name="Nazwa")
    country = models.CharField(max_length=100, verbose_name="Kraj")
    
    def __str__(self):
        return f"{self.name}, {self.country}"
    
    class Meta:
        verbose_name = "Destynacja"
        verbose_name_plural = "Destynacje"


class TravelAgency(models.Model):
    """Model reprezentujący biuro podróży"""
    name = models.CharField(max_length=100, verbose_name="Nazwa")
    website = models.URLField(verbose_name="Strona internetowa")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Biuro podróży"
        verbose_name_plural = "Biura podróży"


class TravelOffer(models.Model):
    """Model reprezentujący ofertę turystyczną"""
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, verbose_name="Destynacja")
    agency = models.ForeignKey(TravelAgency, on_delete=models.CASCADE, verbose_name="Biuro podróży")
    hotel_name = models.CharField(max_length=200, verbose_name="Nazwa hotelu")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cena")
    departure_date = models.DateField(verbose_name="Data wylotu")
    return_date = models.DateField(verbose_name="Data powrotu")
    departure_city = models.CharField(max_length=100, verbose_name="Miasto wylotu")
    duration = models.PositiveIntegerField(verbose_name="Długość pobytu (dni)")
    meal_plan = models.CharField(max_length=100, verbose_name="Wyżywienie")
    has_wifi = models.BooleanField(default=False, verbose_name="Darmowe WiFi")
    has_sunbeds = models.BooleanField(default=False, verbose_name="Darmowe leżaki")
    offer_url = models.URLField(verbose_name="Link do oferty")
    scrape_date = models.DateTimeField(default=timezone.now, verbose_name="Data pobrania")
    
    def __str__(self):
        return f"{self.hotel_name} - {self.destination} ({self.departure_date} - {self.return_date})"
    
    class Meta:
        verbose_name = "Oferta turystyczna"
        verbose_name_plural = "Oferty turystyczne"
        ordering = ['-scrape_date', 'price']
