from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('heat_factor/', views.heat_factor),
]
