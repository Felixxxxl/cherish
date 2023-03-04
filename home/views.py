from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import date,timedelta
from ingredient.models import OwnIngredientDetail
from recipe.models import RecipeDetail,Recipe
from recipe.serializer import RecipeSerializer
from django.db.models import F,Func,FloatField,Case,When,IntegerField,ExpressionWrapper,Avg,Sum,Value
from django.db.models.functions import Exp,Cast,Abs,Power
from .models import IngredientStatusLog
from .serializers import IngredientStatusLogSerializer
# Create your views here.

UNIT_TRANS_DICT = {
    'g': 1,
    'kg':1000,
    'oz':28.35,
    'lbs':453.59
}

def homePage(request):
    return render(request,'home.html')

def logPage(request):
    return render(request,'log.html')

class RecommedRecipesView(APIView):
    def get(self,request,*args, **kwargs):
        quantity_k = 0.3
        expiry_date_k = 0.7

        all_details = OwnIngredientDetail.objects.annotate(
            normalized_quantity = Case(
                    When(quantity_unit='kg',then=F('quantity') * 1000),
                    When(quantity_unit='lbs',then=F('quantity') * 453.59),
                    When(quantity_unit='oz',then=F('quantity') * 28.35),
                    default=F('quantity'),
                    output_field=FloatField()
            )
        )

        today = date.today()
    
        all_details = all_details.annotate(
            remaining_date = ExpressionWrapper((F('expiry_date')-today) / 3600 / 24 / 1000 /1000, output_field = IntegerField())
        )

        all_details = all_details.annotate(
            score = Exp(F('normalized_quantity') * quantity_k /F('remaining_date') / expiry_date_k)
        )

        oi_quantity = all_details.values('ingredient__name').annotate(total_quantity=Sum('normalized_quantity'))

        oi_score = all_details.values('ingredient__name').annotate(avg_score=Avg('score')).order_by("-avg_score")

        oi_list = {}
        for oi in oi_score:
            oi_list[oi.get('ingredient__name')] = oi.get('avg_score')

        oi_quantity_list = {}
        for oi in oi_quantity:
            oi_quantity_list[oi.get('ingredient__name')] = oi.get('total_quantity')


        recipe_details = RecipeDetail.objects.annotate(
            name = F('ingredient__name')
        )

        recipe_details = recipe_details.annotate(
            normalized_quantity = Case(
                    When(unit='kg',then=F('quantity') * 1000),
                    When(unit='lbs',then=F('quantity') * 453.59),
                    When(unit='oz',then=F('quantity') * 28.35),
                    default=F('quantity'),
                    output_field=FloatField()
            ),
            oi_score = Case(
                *[When(name=k,then=Value(v)) for k,v in oi_list.items()],
                defalut=Value(0),
                output_field=FloatField()),

            total_quantity = Case(
                *[When(name=k,then=Value(v)) for k,v in oi_quantity_list.items()],
                defalut=Value(0),
                output_field=FloatField())
        )

        recipe_details =recipe_details.annotate(
            fscore = F('quantity') / F('total_quantity') * F('oi_score')

        )

        fscore = recipe_details.values('recipe__recipe_id').annotate(sum_fscore=Sum('fscore')).order_by("-sum_fscore")[:5]
        print(fscore)
        recipe_list = []
        for item in fscore:
            recipe_list.append(item.get('recipe__recipe_id'))


        recipes = Recipe.objects.filter(recipe_id__in = recipe_list)
        json = RecipeSerializer(recipes, many=True)
        return Response(json.data)


class WastingLogView(APIView):
    def get(self,request,*args, **kwargs):
        log = IngredientStatusLog.objects.all()
        json = IngredientStatusLogSerializer(log,many=True)
        return Response(json.data)
    



