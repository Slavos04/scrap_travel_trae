from django import forms
from django.utils import timezone
from datetime import datetime

class ManualScrapeForm(forms.Form):
    COUNTRY_CHOICES = [
        ('Bułgaria', 'Bułgaria'),
        ('Egipt', 'Egipt'),
        ('Turcja', 'Turcja'),
    ]
    
    countries = forms.MultipleChoiceField(
        label='Kraje',
        choices=COUNTRY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        initial=['Bułgaria', 'Egipt', 'Turcja'],
        required=True
    )
    
    departure_city = forms.CharField(
        label='Miasto wylotu',
        max_length=100,
        initial='Katowice',
        required=True
    )
    
    min_date = forms.DateField(
        label='Data wylotu od',
        initial=datetime(2026, 5, 15).date(),
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    
    min_duration = forms.IntegerField(
        label='Minimalny czas pobytu (dni)',
        min_value=1,
        max_value=30,
        initial=5,
        required=True
    )
    
    max_duration = forms.IntegerField(
        label='Maksymalny czas pobytu (dni)',
        min_value=1,
        max_value=30,
        initial=8,
        required=True
    )
    
    meal_plan = forms.CharField(
        label='Wyżywienie',
        max_length=100,
        initial='All Inclusive',
        required=True
    )
    
    wifi = forms.BooleanField(
        label='Darmowe WiFi',
        initial=True,
        required=False
    )
    
    sunbeds = forms.BooleanField(
        label='Darmowe leżaki',
        initial=True,
        required=False
    )
    
    def clean(self):
        cleaned_data = super().clean()
        min_duration = cleaned_data.get('min_duration')
        max_duration = cleaned_data.get('max_duration')
        
        if min_duration and max_duration and min_duration > max_duration:
            raise forms.ValidationError(
                'Minimalny czas pobytu nie może być większy niż maksymalny czas pobytu.'
            )
        
        return cleaned_data