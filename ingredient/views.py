from .models import OwnIngredient, OwnIngredientDetail
from rest_framework import viewsets
from .serializers import OICategoryCountSerializer, OIDetailSerializer, OICategorySerializer
from django.shortcuts import render,redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from rest_framework import status



class OwnIngredientCategoryView(APIView):
    def get(self,request,*args, **kwargs):
        category = OwnIngredient.objects.all()
        json = OICategoryCountSerializer(category,many=True)
        return Response(json.data)
    
class OwnIngredientDetailsListView(APIView):

    def get(self,request,*args, **kwargs):
        ingredient_id = kwargs.get("ingredient_id")
        try:
            ingredient = OwnIngredient.objects.get(ingredient_id = ingredient_id)
        except OwnIngredient.DoesNotExist:
            raise Http404
        
        try:
            details = OwnIngredientDetail.objects.filter(ingredient = ingredient)
        except OwnIngredientDetail.DoesNotExist:
            raise Http404
        
        json = OIDetailSerializer(details,many=True)
        return Response(json.data)       
    
class OwnIngredientDetailView(APIView):

    def get(self,request,*args, **kwargs):
        detail_id = kwargs.get("detail_id")
        try:
            detail = OwnIngredientDetail.objects.get(detail_id = detail_id)
        except OwnIngredientDetail.DoesNotExist:
            raise Http404
        
        json = OIDetailSerializer(detail)

        return Response(json.data)
    
    def put(self,request,*args,**kwargs):
        data = request.data
        try:
            detail = OwnIngredientDetail.objects.get(detail_id = kwargs.get("detail_id"))
        except OwnIngredientDetail.DoesNotExist:
            raise Http404
        ser_data = OIDetailSerializer(detail,data=data)

        if ser_data.is_valid():
            detail = ser_data.save()
            return Response(ser_data.data)
        else:
            print(ser_data.data)
            print(ser_data.error_messages)
            return Response(ser_data.errors,status=status.HTTP_400_BAD_REQUEST)
        
    def post(self,request,*args, **kwargs):
        data = request.data
        name = data.get('name')
        try:
            ingredient = OwnIngredient.objects.get(name=name)
        except OwnIngredient.DoesNotExist:
            ingredient = OwnIngredient.objects.create(name=name)
        

        ser_data = OIDetailSerializer(data=data,context={'ingredient':ingredient})
        if ser_data.is_valid():
            ser_data.save()
            return Response(ser_data.data)
        else:
            ingredient.delete()
            print(ser_data.error_messages)
            return Response(status=status.HTTP_400_BAD_REQUEST)    

    def delete(self,request,*args, **kwargs):
        detail_id = kwargs.get("detail_id")
        try:
            detail = OwnIngredientDetail.objects.get(detail_id = detail_id)
            ingredient = detail.ingredient
            detail.delete()
            
            details =OwnIngredientDetail.objects.filter(ingredient=ingredient)
            if not details.exists():
                ingredient.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_202_ACCEPTED)
        except OwnIngredientDetail.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
def homePage(request):
    return render(request,'home.html')

def ingredientsPage(request):
    return render(request,'ingredients.html')
