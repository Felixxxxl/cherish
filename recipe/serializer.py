from rest_framework import serializers
from .models import Recipe,RecipeIngredient,RecipeDetail
from datetime import datetime

class RecipeSerializer(serializers.Serializer):
    recipe_id = serializers.IntegerField()
    recipe_name = serializers.CharField()

    class Meta:
        model = Recipe
        fields = '__all__'

class IngredientSerializers(serializers.Serializer):
    ingredient_id = serializers.IntegerField()
    name = serializers.CharField()

    class Meta:
        model = RecipeIngredient
        fields = '__all__'

class RecipeDetailSerializer(serializers.Serializer):
    detail_id = serializers.IntegerField()
    quantity = serializers.FloatField()
    unit = serializers.CharField()
    recipe = RecipeSerializer()
    ingredient = IngredientSerializers()

    class Meta:
        model = RecipeDetail
        fields = '__all__'

class RecipeDetailsListSerializer(serializers.Serializer):
    recipe_id = serializers.IntegerField()
    recipe_name = serializers.CharField()
    details = serializers.SerializerMethodField()

    def get_details(self,obj):
        details = obj.details.all()
        serialized_details = RecipeDetailSerializer(details, many=True).data
        return serialized_details

    class Meta:
        model = Recipe
        fields = '__all__'

