from django.shortcuts import render
from rest_framework.views import APIView
from .models import Recipe,RecipeDetail,RecipeIngredient
from . serializer import RecipeSerializer, IngredientSerializers, RecipeDetailSerializer,RecipeDetailsListSerializer
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

def recipePage(request):
    return render(request,'recipe.html')

class RecipesListView(APIView):
    def get(self,request,*args, **kwargs):
        recipes = Recipe.objects.all()
        json = RecipeSerializer(recipes, many=True)
        return Response(json.data)
    
class RecipeIngreidentView(APIView):
    def get(self,request,*args,**kwargs):
        ingredient_id = kwargs.get('ingredient_id')
        try:
            ingredient = RecipeIngredient.objects.get(ingredient_id = ingredient_id)
        except RecipeIngredient.DoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)
        json = IngredientSerializers(ingredient)
        return Response(json.data)
    
class RecipeDetailView(APIView):
    def get(self,request,*args,**kwargs):
        detail_id = kwargs.get('detail_id')
        try:
            detail = RecipeDetail.objects.get(detail_id=detail_id)
        except RecipeDetail.DoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)
        json = RecipeDetailSerializer(detail)
        return Response(json.data)
    
class RecipeDetailsListView(APIView):
    def get(self,request,*args,**kwargs):
        recipe_id = kwargs.get('recipe_id')
        try:
            recipe = Recipe.objects.get(recipe_id=recipe_id)
        except Recipe.DoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)
        json = RecipeDetailsListSerializer(recipe)
        return Response(json.data)
    