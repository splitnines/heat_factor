from django.urls import path
from django.views.generic import RedirectView

from .views import *

urlpatterns = [
    path('', home_view),
    path('points/', points_view),
    path('heat_factor/', heat_factor_view),
    path('bad_url/', bad_url_view),
    path('get_upped/', get_upped_view),
    path('error/', error_view),
    path('pps/', pps_view),
    path(
        'favicon\.ico', RedirectView.as_view(url='/static/images/favicon.ico')
    ),
]
