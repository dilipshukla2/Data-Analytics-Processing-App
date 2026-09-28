# processor/serializers.py
from rest_framework import serializers
from .models import AggregatedResult

class AggregatedResultSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True)

    class Meta:
        model = AggregatedResult
        fields = ['category_name', 'region_name', 'total_amount', 'transaction_count', 'anomaly_score']