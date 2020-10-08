from django.urls import path, include
from django.views.generic import RedirectView

from .views import (
    home_view, points_view, heat_factor_view, bad_url_view,
    get_upped_view, error_view, pps_view
)
from heat_factor.views import UspsaViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'uspsa', UspsaViewSet)

urlpatterns = [
    path('', home_view),
    path('heat_factor/', heat_factor_view),
    path('get_upped/', get_upped_view),
    path('points/', points_view),
    path('pps/', pps_view),
    path('bad_url/', bad_url_view),
    path('error/', error_view),
    path('', include(router.urls)),
    path(r'favicon\.ico',
         RedirectView.as_view(url='/static/images/favicon.ico')),
]
