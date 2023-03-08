from rest_framework import serializers
from .models import IngredientStatusLog

class IngredientStatusLogSerializer(serializers.Serializer):
    """
    A serializer class representing ingredient waste log.

    """
    log_id = serializers.IntegerField()
    ingredient_name = serializers.CharField()
    quantity = serializers.FloatField()
    date = serializers.DateField()


    class Meta:
        model = IngredientStatusLog
        fields = '__all__'