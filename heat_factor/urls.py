from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.home),
    path('points/', views.points),
    path('heat_factor/', views.heat_factor),
    path('bad_url/', views.bad_url),
    path('get_upped/', views.get_upped),
    path('error/', views.error),
    path('pps/', views.pps),
    # path('COVID-19_data_analysis', views.covid_da),
    path('favicon\.ico', RedirectView.as_view(url='/static/images/favicon.ico')),
]
