from rest_framework import serializers
from .models import Recipe, RecipeIngredient, RecipeDetail

class RecipeSerializer(serializers.Serializer):
    """
    A serializer class representing a recipe.

    """
    recipe_id = serializers.IntegerField()
    recipe_name = serializers.CharField()

    class Meta:
        model = Recipe
        fields = '__all__'


class IngredientSerializers(serializers.Serializer):
    """ 
    A serializer class representing an ingredient.

    """
    ingredient_id = serializers.IntegerField()
    name = serializers.CharField()

    class Meta:
        model = RecipeIngredient
        fields = '__all__'


class RecipeDetailSerializer(serializers.Serializer):
    """ 
    A serializer class representing the detail ingredient of a recipe.
    
    """
    detail_id = serializers.IntegerField()
    quantity = serializers.FloatField()
    unit = serializers.CharField()
    recipe = RecipeSerializer(required=False)
    ingredient = IngredientSerializers(required=False)

    def update(self, instance, validated_data):
        """
        Method to update the instance of RecipeDetail model with validated data.

        params:
        instance: The object to be updated
        validated_data: The validated data.

        return:
        The updated instance of the model.
        """
        instance.quantity = validated_data.get('quantity')
        instance.unit = validated_data.get('unit')
        ingredient_id = validated_data.get('ingredient').get('ingredient_id')
        ingredient = RecipeIngredient.objects.get(ingredient_id=ingredient_id)
        instance.ingredient = ingredient
        instance.save()
        return instance

    class Meta:
        model = RecipeDetail
        fields = '__all__'


class RecipeDetailsListSerializer(serializers.Serializer):
    """
    A serializer class representing the details inside Recipe.

    """
    recipe_id = serializers.IntegerField()
    recipe_name = serializers.CharField()
    details = serializers.SerializerMethodField()

    def get_details(self, obj):
        """ 
    
        Method to get the serialization of Recipe details

        params:
        obj: Recipe object

        return:
        The serialization of recipe details

        """
        details = obj.details.all()
        serialized_details = RecipeDetailSerializer(details, many=True).data
        return serialized_details

    class Meta:
        model = Recipe
        fields = '__all__'
