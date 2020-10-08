from .models import AdminHoneypotLoginattempt

from rest_framework import viewsets
from rest_framework import permissions
from .serializers import AdminHoneyPotSerializer


class AdminHoneyPotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdminHoneypotLoginattempt.objects.all().order_by('-timestamp')
    serializer_class = AdminHoneyPotSerializer
    permission_classes = [permissions.IsAuthenticated]
