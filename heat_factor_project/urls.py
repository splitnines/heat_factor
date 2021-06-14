from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', include('admin_honeypot.urls',
         namespace='admin_honeypot')),
    path('mgnt', admin.site.urls),
    path('api-auth/', include('rest_framework.urls',
                              namespace='rest_framework')),
    path('', include('heat_factor.urls')),
    path('', include('admin_honeypot_fix.urls')),
    path('', include('grid_iron.urls')),
    path(
        'robots.txt',
        TemplateView.as_view(
            template_name='robots.txt', content_type="text/plain"
        ),
    ),
    path(
        'grid_iron_teamdb.csv',
        TemplateView.as_view(
            template_name='grid_iron_teamdb.csv', content_type="text/plain"
        ),
    ),
]
