from .models import AdminHoneypotLoginattempt
from rest_framework import serializers


class AdminHoneyPotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AdminHoneypotLoginattempt
        fields = [
            'username', 'session_key', 'user_agent', 'timestamp',
            'path', 'ip_address'
        ]
