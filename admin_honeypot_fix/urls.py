from django.urls import include, path
from rest_framework import routers

from .views import AdminHoneyPotViewSet

router = routers.DefaultRouter()
router.register(r'honeypot', AdminHoneyPotViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
