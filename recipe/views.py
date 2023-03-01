from django.shortcuts import render
from rest_framework.views import APIView
from .models import Recipe, RecipeDetail, RecipeIngredient
from . serializer import RecipeSerializer, IngredientSerializers, RecipeDetailSerializer, RecipeDetailsListSerializer
from rest_framework.response import Response
from rest_framework import status
import json
from django.db import transaction

# Create your views here.


def recipePage(request):
    return render(request, 'recipe.html')


class RecipesListView(APIView):
    def get(self, request, *args, **kwargs):
        recipes = Recipe.objects.all()
        json = RecipeSerializer(recipes, many=True)
        return Response(json.data)


class RecipeIngreidentView(APIView):
    def get(self, request, *args, **kwargs):
        ingredient_id = kwargs.get('ingredient_id')
        try:
            ingredient = RecipeIngredient.objects.get(
                ingredient_id=ingredient_id)
        except RecipeIngredient.DoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)
        json = IngredientSerializers(ingredient)
        return Response(json.data)


class RecipeDetailView(APIView):
    def get(self, request, *args, **kwargs):
        detail_id = kwargs.get('detail_id')
        try:
            detail = RecipeDetail.objects.get(detail_id=detail_id)
        except RecipeDetail.DoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)
        json = RecipeDetailSerializer(detail)
        return Response(json.data)


class RecipeInfoView(APIView):
    def get(self, request, *args, **kwargs):
        recipe_id = kwargs.get('recipe_id')
        try:
            recipe = Recipe.objects.get(recipe_id=recipe_id)
        except Recipe.DoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)
        json = RecipeDetailsListSerializer(recipe)
        return Response(json.data)


class RecipeDetailsListView(APIView):
    def get(self, request, *args, **kwargs):
        recipe_id = kwargs.get('recipe_id')
        try:
            recipe = Recipe.objects.get(recipe_id=recipe_id)
            details = RecipeDetail.objects.filter(recipe=recipe)
        except RecipeDetail.DoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)
        json = RecipeDetailSerializer(details, many=True)
        return Response(json.data)


class TestView(APIView):
    @transaction.atomic
    def put(self, request, *args, **kwargs):

        data = json.loads(request.body)
        details = data.get('details')
        recipe_id = data.get('recipe_id')
        save_id = transaction.savepoint()
        

        try:
            recipe = Recipe.objects.get(recipe_id=recipe_id)

        except Recipe.DoesNotExist:

            return Response(status=status.HTTP_404_NOT_FOUND)
        
        detail_id_list = []
        
        ori_detail_id_list = []

        details_db = RecipeDetail.objects.filter(recipe = recipe)

        for detail in details_db:

            ori_detail_id_list.append(detail.detail_id)


        for detail in details:

            if detail.get('detail_id') == 'newRow':
                if detail.get('quantity') == '':
                    continue
                ingredient_name = detail.get('ingredient').get('name')
                try:
                    ingredient = RecipeIngredient.objects.get(
                        name=ingredient_name)
                except RecipeIngredient.DoesNotExist:
                    ingredient = RecipeIngredient.objects.create(
                        name=ingredient_name)

                detail = RecipeDetail.objects.create(
                    recipe=recipe, ingredient=ingredient, quantity=detail.get('quantity'), unit=detail.get('unit'))

            else:
                detail_id = detail.get('detail_id')
                detail_id_list.append(detail_id)
                ingredient_name = detail.get('ingredient').get('name')
                try:
                    ingredient = RecipeIngredient.objects.get(
                        name=ingredient_name)
                except RecipeIngredient.DoesNotExist:
                    ingredient = RecipeIngredient.objects.create(
                        name=ingredient_name)

                detail['ingredient']['ingredient_id'] = ingredient.ingredient_id
                try:
                    detail_db = RecipeDetail.objects.get(detail_id=detail_id)
                except RecipeDetail.DoesNotExist:
                    transaction.savepoint_rollback(save_id)
                    return Response(status=status.HTTP_404_NOT_FOUND)

                ser_data = RecipeDetailSerializer(detail_db, data=detail)

                if ser_data.is_valid():
                    ser_data.save()
                else:
                    print(ser_data.errors)
                    transaction.savepoint_rollback(save_id)
                    return Response(status=status.HTTP_404_NOT_FOUND)
                
        del_detail_id_list = []
        for id in ori_detail_id_list:
            id_int = str(id)
            if id_int not in detail_id_list:
                del_detail_id_list.append(id_int)

        for id in del_detail_id_list:
            try:
                detail = RecipeDetail.objects.get(detail_id = id)
            except RecipeDetail.DoesNotExist:
                continue

            detail.delete()

        
        return Response(data={'success':True})
    
    @transaction.atomic
    def post(self,request,*args, **kwargs):
        return Response(status=status.HTTP_200_OK)

