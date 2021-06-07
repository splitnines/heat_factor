from django.urls import path, include
from django.views.generic import RedirectView

from .views import (
    grid_iron_view
)


urlpatterns = [
    path('grid_iron_calc/', grid_iron_view),
    path(
        r'favicon\.ico', RedirectView.as_view(url='/static/images/favicon.ico')
    ),
]