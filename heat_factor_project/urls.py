from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', include('admin_honeypot.urls',
         namespace='admin_honeypot')),
    path('mgnt', admin.site.urls),
    path('api-auth/', include('rest_framework.urls',
                              namespace='rest_framework')),
    path('', include('heat_factor.urls')),
    path('', include('admin_honeypot_fix.urls')),
]
