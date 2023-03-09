from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import date, timedelta
from ingredient.models import OwnIngredientDetail, OwnIngredient
from recipe.models import RecipeDetail, Recipe
from recipe.serializer import RecipeSerializer
from django.db.models import F, Func, FloatField, Case, When, IntegerField, ExpressionWrapper, Avg, Sum, Value, Q
from django.db.models.functions import Exp, Cast, Abs, Power
from .models import IngredientStatusLog
from .serializers import IngredientStatusLogSerializer
# Create your views here.

UNIT_TRANS_DICT = {
    'g': 1,
    'kg': 1000,
    'oz': 28.35,
    'lbs': 453.59
}


def homePage(request):
    return render(request, 'home.html')


def logPage(request):
    return render(request, 'log.html')

# Create a RecommedRecipesView that inherits APIView to handle HTTP GET request.


class RecommendRecipesView(APIView):
    """ 
    A view to handle HTTP GET requests to recommend recipes 

    HTTP Methods:
    - GET: Handles GET requests to recommend recipes
    """

    def get(self, request, *args, **kwargs):
        """
        A method that handles GET requests to recommend recipes

        Parameters:
        - request: The request object.

        Returns:
        - Response: Recommended recipe(s) serialized as JSON objects
        """

        # Define the scoring coefficient, quality coefficient and time coefficient
        quantity_k = 0.3
        expiry_date_k = 0.7

        # Convert the quality of the ingredients in the existing ingredients to gram
        all_details = OwnIngredientDetail.objects.annotate(
            normalized_quantity=Case(
                When(quantity_unit='kg', then=F('quantity') * 1000),
                When(quantity_unit='lbs', then=F('quantity') * 453.59),
                When(quantity_unit='oz', then=F('quantity') * 28.35),
                default=F('quantity'),
                output_field=FloatField()
            )

        ).annotate(
            # Calculate the remaining days of the existing ingredients
            remaining_date=ExpressionWrapper(
                (F('expiry_date')-date.today()) / 3600 / 24 / 1000 / 1000, output_field=IntegerField())

        ).annotate(
            # Use the quality of the ingredients and the expiration date of the ingredients to score the ingredients
            # Formula: socre = exp(quantity * quality coefficient / (remaining days * time coefficient))
            score=Exp(F('normalized_quantity') * quantity_k / \
                      F('remaining_date') / expiry_date_k)
        )

        # Statistics the total quality of the same type of ingredients
        oi_quantity = all_details.values('ingredient__name').annotate(
            total_quantity=Sum('normalized_quantity'))

        # Statistics the average score of the same type of ingredients
        oi_score = all_details.values('ingredient__name').annotate(
            avg_score=Avg('score')).order_by("-avg_score")

        # Output the above calculation into a dictionary form
        oi_score_list = {oi.get('ingredient__name'): oi.get(
            'avg_score') for oi in oi_score}
        oi_quantity_list = {oi.get('ingredient__name'): oi.get(
            'total_quantity') for oi in oi_quantity}

        # Filter recipes with existing ingredients and return recipe arrays
        recipes = Recipe.objects.all()
        recipes_list = []
        for recipe in recipes:

            details = RecipeDetail.objects.filter(recipe=recipe)
            ingredients_enough = True
            for detail in details:

                try:
                    OwnIngredient.objects.get(name=detail.ingredient.name)
                except:
                    ingredients_enough = False
                    break

            if ingredients_enough == True:
                recipes_list.append(recipe)

        recipe_details = RecipeDetail.objects.filter(recipe__in=recipes_list)

        recipe_details = recipe_details.annotate(
            # Format recipe name
            name=F('ingredient__name')
        ).annotate(
            # The quality in the recipes is converted to gram
            normalized_quantity=Case(
                When(unit='kg', then=F('quantity') * 1000),
                When(unit='lbs', then=F('quantity') * 453.59),
                When(unit='oz', then=F('quantity') * 28.35),
                default=F('quantity'),
                output_field=FloatField()
            ),
            # Each ingredient in the recipe corresponds to the score of the own ingredients
            oi_score=Case(
                *[When(name=k, then=Value(v))
                  for k, v in oi_score_list.items()],
                defalut=Value(0),
                output_field=FloatField()),
            # Each ingredient in the recipe corresponds to the total quantity of the own ingredients
            total_quantity=Case(
                *[When(name=k, then=Value(v))
                  for k, v in oi_quantity_list.items()],
                defalut=Value(0),
                output_field=FloatField())
            # Calculate the score of each ingredient in the recipe
        ).annotate(
            fscore=F('quantity') / F('total_quantity') * F('oi_score')

        )

        # Find recipe ids that require more ingredients than own ingredients
        excluded_recipes_id = recipe_details.filter(
            normalized_quantity__gt=F('total_quantity')).values('recipe__recipe_id')
        # Exclude recipes that do not satisfy own ingredient
        recipe_details = recipe_details.exclude(
            Q(recipe__recipe_id__in=excluded_recipes_id))
        # Group and aggregate the scores of all the ingredients in the recipe, and filter out the top 5 recipes with the highest scores
        fscore = recipe_details.values('recipe__recipe_id').annotate(
            sum_fscore=Sum('fscore')).order_by("-sum_fscore")[:5]

        # Add the recipe id just filtered to the array
        recipe_list = list(fscore.values_list('recipe__recipe_id', flat=True))

        recipes = Recipe.objects.filter(recipe_id__in=recipe_list)
        json = RecipeSerializer(recipes, many=True)
        return Response(json.data)


# Create a WastingLogView that inherits APIView to handle HTTP GET request.
class WastingLogView(APIView):
    """ 
    A view to handle HTTP GET requests for IngredientStatusLog model.

    HTTP Methods:
    - GET: Returns JSON serialized data of all objects in IngredientStatusLog model.

    """

    # Define get method to handle GET requests made to the API endpoint url.
    def get(self, request, *args, **kwargs):
        """
        Get all objects in the IngredientStatusLog model from database.
        Serialize each object using IngredientStatusLogSerializer.
        Retrieve all serialized objects as list of JSON serialized data.

        Parameters:
        - request: The request object.

        Returns:
        - Response: A JSON response object containing the list of serialized data.
        """

        # Query IngredientStatusLog model to retrieve all logs in the database.
        logs = IngredientStatusLog.objects.all()

        # Serialize the data returned by the query into JSON format.
        serializer = IngredientStatusLogSerializer(logs, many=True)

        # Return the serialized data as a response with status 200 (OK).
        return Response(serializer.data)

# The following class obtain a list of IngredientStatusLog objects


class WastingLogChartView(APIView):
    """ 

    This view handles HTTP GET requests to retrieve data for ingredient wasting logs chart.

    HTTP Methods:
    - GET: Retrieves and returns waste log data with labels and data values.

    """

    # The method handles GET requests and retrieve data log from the database
    def get(self, request, *args, **kwargs):
        """

        Retrieves all objects from the IngredientStatusLog model, and extracts their ingredient name and quantity.
        Formats the extracted data into two lists containing the ingredient names and corresponding quantities.
        Returns a JSON response object containing 'labels' and 'data' fields with the formatted data.

        Parameters:
        - request: The request object.

        Returns:
        - Response: A JSON response object containing 'label' and 'data' fields.
        """

        # Query objects, group by ingredient name and calculate sum of corresponding quantities
        logs = IngredientStatusLog.objects.values(
            'ingredient_name').annotate(sum_quantity=Sum('quantity'))

        # Retrieve two lists with ingredients names and its corresponding quanitity
        name_quantity_tuples = [
            (log['ingredient_name'], log['sum_quantity']) for log in logs]
        labels, data = zip(*name_quantity_tuples)

        # Return HTTP response with 'data' and 'labels' fields containing quantity and ingedients names.
        return Response({"label": labels, "data": data})
