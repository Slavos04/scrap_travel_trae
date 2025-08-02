from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('offers/', views.OfferListView.as_view(), name='offer_list'),
    path('offers/<int:pk>/', views.OfferDetailView.as_view(), name='offer_detail'),
    path('manual-scrape/', views.ManualScrapeView.as_view(), name='manual_scrape'),
    path('run-scraper/', views.run_scraper_view, name='run_scraper'),
]