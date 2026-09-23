from rest_framework import serializers

class RawDataItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    value = serializers.FloatField()
    is_valid = serializers.BooleanField()

class RawDataSerializer(serializers.Serializer):
    data = RawDataItemSerializer(many=True) 