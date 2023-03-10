from django.test import TestCase,Client
from rest_framework.test import APIClient
from .models import IngredientStatusLog
from .serializers import IngredientStatusLogSerializer
from recipe.models import Recipe,RecipeDetail,RecipeIngredient
from ingredient.models import OwnIngredient,OwnIngredientDetail
from datetime import date,timedelta
from rest_framework import status

class ModelsTestCase(TestCase):
    def setUp(self):
        IngredientStatusLog.objects.create(
            ingredient_name='Beef',
            quantity=0.2,
            date=date.today()
        )

    def test_ingredient_status_log(self):
        # Retrieving the log from the database
        log = IngredientStatusLog.objects.get(ingredient_name='Beef')
        
        # Testing if the log was created correctly
        self.assertEqual(log.quantity, 0.2)
        self.assertEqual(log.date, date.today())


class SerializersTestCase(TestCase):
    def setUp(self):
        self.log = IngredientStatusLog.objects.create(
            ingredient_name='Salt',
            quantity=1.5,
            date=date.today()
        )
        
    def test_log_serializer(self):
        serializer = IngredientStatusLogSerializer(self.log)
        data = serializer.data

        self.assertEqual(data['ingredient_name'], self.log.ingredient_name)
        self.assertEqual(data['quantity'], self.log.quantity)
        self.assertEqual(data['date'], str(date.today()))

class TestHomePage(TestCase):

    def test_home_page(self):
        client = Client()
        response = client.get('/home/')
        self.assertEqual(response.status_code, 200)

class TestLogPage(TestCase):

    def test_log_page(self):
        client = Client()
        response = client.get('/log/')
        self.assertEqual(response.status_code, 200)

### API UNITTEST ###
class WastingLogViewTestCase(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.log1 = IngredientStatusLog.objects.create(
            ingredient_name='Tomato',
            quantity=2.5,
            date='2022-01-03'
        )
        self.log2 = IngredientStatusLog.objects.create(
            ingredient_name='Onion',
            quantity=1.25,
            date='2022-01-04'
        )

    def test_get_all_logs(self):
        response = self.client.get('/api/home/wastelog/')
        logs = IngredientStatusLog.objects.all()
        serializer = IngredientStatusLogSerializer(logs, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

class WastingLogChartViewTestCase(TestCase):
    def setUp(self):
        
        # Define some objects to add to the recipe inventory
        log1 = IngredientStatusLog.objects.create(
            ingredient_name='olive oil',
            quantity=0.25,
            date='2022-01-03',
        )
        log2 = IngredientStatusLog.objects.create(
            ingredient_name='eggs',
            quantity=1.5,
            date='2022-01-03',
        )

        # Instantiate APIClient to simulate HTTP requests
        self.client = APIClient()

    def test_get_waste_log_data(self):

        # Request data using GET method through client
        response = self.client.get('/api/home/wastelogchart/')

        # Check expected status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("label", response.json())
        self.assertIn("data", response.json())

        # Check the data values returned
        self.assertEqual(len(response.json()["label"]), 2)
        self.assertEqual(len(response.json()["data"]), 2)

class RecommendRecipesViewTestCase(TestCase):
    def setUp(self):
        self.recipe1 = Recipe.objects.create(recipe_name='Pancakes1')
        self.ingredient1 = RecipeIngredient.objects.create(name='flour')
        self.ingredient2 = RecipeIngredient.objects.create(name='water')

        self.detail1 = RecipeDetail.objects.create(ingredient=self.ingredient1,
                                                    recipe=self.recipe1,
                                                    quantity=500,
                                                    unit='g')
        self.detail2 = RecipeDetail.objects.create(ingredient=self.ingredient2,
                                                    recipe=self.recipe1,
                                                    quantity=300,
                                                    unit='g',)

        self.recipe2 = Recipe.objects.create(recipe_name='Pancakes2')

        self.detail3 = RecipeDetail.objects.create(ingredient=self.ingredient1,
                                                    recipe=self.recipe2,
                                                    quantity=800,
                                                    unit='g')
        self.detail4 = RecipeDetail.objects.create(ingredient=self.ingredient2,
                                                    recipe=self.recipe2,
                                                    quantity=900,
                                                    unit='g',)

        self.recipe3 = Recipe.objects.create(recipe_name='Pancakes3')

        self.detail5 = RecipeDetail.objects.create(ingredient=self.ingredient1,
                                                    recipe=self.recipe3,
                                                    quantity=300,
                                                    unit='g')
        self.detail6 = RecipeDetail.objects.create(ingredient=self.ingredient2,
                                                    recipe=self.recipe3,
                                                    quantity=1500,
                                                    unit='g',)
        # Own Ingredient
        self.owningredient1 = OwnIngredient.objects.create(name='flour')
        self.owningredient2 = OwnIngredient.objects.create(name='water')
        self.oidetail1 = OwnIngredientDetail.objects.create(ingredient=self.owningredient1,quantity=1000,quantity_unit='g',expiry_date=date.today() + timedelta(days=5))
        self.oidetail2 = OwnIngredientDetail.objects.create(ingredient=self.owningredient2,quantity=1000,quantity_unit='g',expiry_date=date.today() + timedelta(days=5))

    def test_recommend_recipe(self):
        response = self.client.get('/api/home/recommended/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["recipe_id"], self.recipe2.recipe_id)
        self.assertEqual(response.data[1]["recipe_id"], self.recipe1.recipe_id)
        self.assertEqual(len(response.data), 2)
