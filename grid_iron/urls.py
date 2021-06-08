from django.urls import path, include
from django.views.generic import RedirectView

from .views import (
    grid_iron_view
)

from grid_iron.views import GridironViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'gridiron', GridironViewSet)


urlpatterns = [
    path('grid_iron_calc/', grid_iron_view),
    path('', include(router.urls)),
    path(
        r'favicon\.ico', RedirectView.as_view(url='/static/images/favicon.ico')
    ),
]