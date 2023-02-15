from rest_framework.serializers import Serializer
from rest_framework import serializers

class OwnIngredientsSerializers(Serializer):
    type = serializers.CharField(required = True, max_length = 64)
    name = serializers.CharField(required = True, max_length = 64)
    amount = serializers.FloatField(required = True)
    unit = serializers.CharField(required = True, max_length = 12)
    expiration_date = serializers.DateField(required = True, format='%Y-%m-%d')