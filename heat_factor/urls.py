from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('points/', views.points),
    path('heat_factor/', views.heat_factor),
    path('bad_url/', views.bad_url),
    path('get_upped/', views.get_upped),
    path('login_error/', views.login_error),
]
