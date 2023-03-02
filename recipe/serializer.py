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
    recipe = RecipeSerializer(required=False)
    ingredient = IngredientSerializers(required=False)

    def update(self,instance,validated_data):
        instance.quantity = validated_data.get('quantity')
        instance.unit = validated_data.get('unit')
        ingredient_id = validated_data.get('ingredient').get('ingredient_id')
        ingredient = RecipeIngredient.objects.get(ingredient_id=ingredient_id)
        instance.ingredient = ingredient
        instance.save()
        return instance
    
    # def create(self, validated_data):
        # detail = OwnIngredientDetail.objects.create(ingredient = self.context['ingredient'],**validated_data)
        # return detail

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

