from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import date,timedelta
from ingredient.models import OwnIngredientDetail,OwnIngredient
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

# Create a RecommedRecipesView that inherits APIView to handle HTTP GET request.
class RecommedRecipesView(APIView):
    def get(self,request,*args, **kwargs):

        # Filter recipes with existing ingredients and return recipe arrays
        recipes = Recipe.objects.all()
        recipes_list = []
        for recipe in recipes:
            
            details = RecipeDetail.objects.filter(recipe=recipe)
            ingredient_enough = True
            for detail in details:

                try:
                    OwnIngredient.objects.get(name=detail.ingredient.name)
                except:
                    ingredient_enough =False
                    break
            
            if ingredient_enough == True:
                recipes_list.append(recipe)

        # Define the scoring coefficient, quality coefficient and time coefficient
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

        recipe_details = RecipeDetail.objects.filter(recipe__in=recipes_list)


        recipe_details = recipe_details.annotate(
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

        

        recipe_details = recipe_details.filter(quantity__lt=F('total_quantity'))

        recipe_details =recipe_details.annotate(
            fscore = F('quantity') / F('total_quantity') * F('oi_score')

        )

        fscore = recipe_details.values('recipe__recipe_id').annotate(sum_fscore=Sum('fscore')).order_by("-sum_fscore")[:5]

        recipe_list = []
        for item in fscore:
            recipe_list.append(item.get('recipe__recipe_id'))


        recipes = Recipe.objects.filter(recipe_id__in = recipe_list)
        json = RecipeSerializer(recipes, many=True)
        return Response(json.data)


# Create a WastingLogView that inherits APIView to handle HTTP GET request.
class WastingLogView(APIView):

    # Define get method to handle GET requests made to the API endpoint url.
    def get(self,request,*args, **kwargs):

        # Query IngredientStatusLog model to retrieve all logs in the database.
        logs = IngredientStatusLog.objects.all()

        # Serialize the data returned by the query into JSON format.
        serializer = IngredientStatusLogSerializer(logs, many=True)

        # Return the serialized data as a response with status 200 (OK).
        return Response(serializer.data)

# The following class obtain a list of IngredientStatusLog objects 
class WastingLogChartView(APIView):

    # The method handles GET requests and retrieve data log from the database
    def get(self, request, *args, **kwargs):
        
        # Query objects, group by ingredient name and calculate sum of corresponding quantities
        logs = IngredientStatusLog.objects.values('ingredient_name').annotate(sum_quantity=Sum('quantity'))

        # Retrieve two lists with ingredients names and its corresponding quanitity
        name_quantity_tuples = [(log['ingredient_name'], log['sum_quantity']) for log in logs]
        labels, data = zip(*name_quantity_tuples)

        # Return HTTP response with 'data' and 'labels' fields containing quantity and ingedients names.
        return Response({"label": labels, "data": data})
    



