from .models import Gridiron
from rest_framework import serializers


class GridironSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Gridiron
        fields = [
            'id', 'team_name', 'team_mem1', 'team_mem2', 'team_mem3'
        ]
