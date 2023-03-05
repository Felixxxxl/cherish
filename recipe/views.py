from django.shortcuts import render
from rest_framework.views import APIView
from .models import Recipe, RecipeDetail, RecipeIngredient
from . serializer import RecipeSerializer, IngredientSerializers, RecipeDetailSerializer, RecipeDetailsListSerializer
from rest_framework.response import Response
from rest_framework import status
import json
from django.db import transaction
from ingredient.models import OwnIngredient, OwnIngredientDetail
from ingredient.serializers import OICategoryCountSerializer
from django.db.models import F, Case, When, Value, CharField

# Create your views here.
UNIT_TRANS_DICT = {
    'g': 1,
    'kg':1000,
    'oz':28.35,
    'lbs':453.59
}

def recipePage(request):
    return render(request, 'recipe.html')


class RecipesListView(APIView):
    def get(self, request, *args, **kwargs):
        recipes = Recipe.objects.all()
        json = RecipeSerializer(recipes, many=True)
        return Response(json.data)


class RecipeIngredientView(APIView):
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
    
    def delete(self,request,*args, **kwargs):
        recipe_id = kwargs.get("recipe_id")
        try:
            recipe = Recipe.objects.get(recipe_id = recipe_id)  
        except Recipe.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        details =RecipeDetail.objects.filter(recipe=recipe)
        details.delete()
        recipe.delete()
        return Response(data={"success":True})


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
        data = json.loads(request.body)
        details = data.get('details')
        recipe_name = data.get('recipe_name')
        save_id = transaction.savepoint()

        try:
            recipe = Recipe.objects.create(recipe_name = recipe_name)
        except Exception as e:
            transaction.savepoint_rollback(save_id)
            return Response({"errors":e})
        
        

        for detail in details:
            
            if detail.get('quantity') == '' or detail.get('ingredient').get('name') == '':
                transaction.savepoint_rollback(save_id)
                return Response(status=status.HTTP_204_NO_CONTENT)
            quantity = detail.get('quantity')
            unit = detail.get('unit')
            ingredient_name = detail.get('ingredient').get('name')



            try:
                ingredient = RecipeIngredient.objects.get(name = ingredient_name)
            except Exception as e:
                ingredient = RecipeIngredient.objects.create(name = ingredient_name)

            try:
                ingredient_detail = RecipeDetail.objects.create(recipe= recipe,ingredient=ingredient,quantity=quantity,unit=unit)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"errors":e})

        return Response(data={'success':True})
    

class RecipeDetailCheckView(APIView):
    def get(self,request,*args, **kwargs):
        recipe_id = kwargs.get('recipe_id')

        try:
            recipe = Recipe.objects.get(recipe_id=recipe_id)
            details = RecipeDetail.objects.filter(recipe=recipe)
        except RecipeDetail.DoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)
        
        recipe_name = recipe.recipe_name
        response = {'recipe_name':recipe_name,
                    'all_enough':True,
                    'details':[]}

        for detail in details:

            detail_dict = {'ingredient_name':'',
                           'origin_quantity':'',
                           'unit':'',
                           'after_quantity':'',
                           'enough':True}

            detail_dict['ingredient_name'] = detail.ingredient.name

            
            recipe_unit = detail.unit
            recipe_quantity = detail.quantity
            try:
                ingredient = OwnIngredient.objects.get(name = detail.ingredient.name)
                count_detail = OICategoryCountSerializer(ingredient)
                oi_unit = count_detail.data['quantity_and_unit']['total_quantity_unit']
                oi_quantity = count_detail.data['quantity_and_unit']['total_quantity'] * UNIT_TRANS_DICT[oi_unit] / UNIT_TRANS_DICT[recipe_unit]
            except OwnIngredient.DoesNotExist:
                response['all_enough'] = False
                detail_dict['enough'] = False
                oi_quantity = 0

            diff = oi_quantity - recipe_quantity

            if diff < 0 :
                detail_dict['enough'] = False
                response['all_enough'] = False

            detail_dict['unit'] = recipe_unit
            detail_dict['origin_quantity'] = oi_quantity
            detail_dict['after_quantity'] = diff

            response['details'].append(detail_dict)

        return Response(data=response)
    
    @transaction.atomic
    def put(self,request,*args, **kwargs):
        save_id = transaction.savepoint()
        data = json.loads(request.body)
        recipe_id = data.get('recipe_id')

        try:
            recipe = Recipe.objects.get(recipe_id=recipe_id)
            details = RecipeDetail.objects.filter(recipe=recipe)
        except RecipeDetail.DoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)
        
        for detail in details:

            ingredient_name = detail.ingredient.name

            try:
                ingredient = OwnIngredient.objects.get(name = ingredient_name)
            except OwnIngredient.DoesNotExist:
                transaction.savepoint_rollback(save_id)
                return Response(status.HTTP_404_NOT_FOUND)

            try:
                details_db = OwnIngredientDetail.objects.filter(ingredient=ingredient)
                details_db = details_db.annotate(
                    normalized_quantity = Case(
                    When(quantity_unit='kg',then=F('quantity') * 1000),
                    When(quantity_unit='lbs',then=F('quantity') * 453.59),
                    When(quantity_unit='oz',then=F('quantity') * 28.35),
                    default=F('quantity'),
                    output_field=CharField()
                    )
                ).order_by('expiry_date','normalized_quantity')
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response(status.HTTP_404_NOT_FOUND)

            count_quantity = detail.quantity * UNIT_TRANS_DICT[detail.unit]
            try:

                for detail_db in details_db:
                    quantity = detail_db.quantity * UNIT_TRANS_DICT[detail_db.quantity_unit]
                    if quantity > count_quantity:
                        detail_db.quantity = (quantity - count_quantity) / UNIT_TRANS_DICT[detail_db.quantity_unit]
                        detail_db.save()
                        break
                    else:
                        count_quantity = count_quantity - quantity
                        detail_db.delete()
                        print('del')

            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response(status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_200_OK)
    

    

