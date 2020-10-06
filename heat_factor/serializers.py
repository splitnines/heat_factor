from .models import Uspsa
from rest_framework import serializers


class UspsaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Uspsa
        fields = [
            'id', 'uspsa_num', 'division', 'date_created', 'date_updated'
        ]
