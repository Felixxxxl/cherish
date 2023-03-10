from django.test import TestCase,Client
from rest_framework.test import APIClient
from rest_framework import status
from .models import Recipe, RecipeIngredient, RecipeDetail
from ingredient.models import OwnIngredient,OwnIngredientDetail
from .serializers import RecipeSerializer, IngredientSerializers, RecipeDetailSerializer, RecipeDetailsListSerializer

class ModelsTestCase(TestCase):
    def setUp(self):
        self.recipe1 = Recipe.objects.create(recipe_name='Pancakes')
        self.ingredient1 = RecipeIngredient.objects.create(name='Flour')
        self.recipe_detail1 = RecipeDetail.objects.create(
            recipe=self.recipe1,
            ingredient=self.ingredient1,
            quantity=1.5,
            unit='kg'
        )

    def test_recipe_model(self):
        pancake_recipe = Recipe.objects.get(recipe_id=1)
        self.assertEqual(pancake_recipe.recipe_name, 'Pancakes')

    def test_ingredient_model(self):
        flour_ingredient = RecipeIngredient.objects.get(ingredient_id=1)
        self.assertEqual(flour_ingredient.name, 'Flour')

    def test_recipe_detail_model(self):
        pancake_recipe_detail = RecipeDetail.objects.get(detail_id=1)
        self.assertEqual(pancake_recipe_detail.recipe, self.recipe1)
        self.assertEqual(pancake_recipe_detail.ingredient, self.ingredient1)
        self.assertEqual(pancake_recipe_detail.quantity, 1.5)
        self.assertEqual(pancake_recipe_detail.unit, 'kg')

class RecipeSerializerTest(TestCase):
    
    def setUp(self):
        self.recipe = Recipe.objects.create(recipe_name='Pancakes')
        self.serializer_data = {'recipe_id': self.recipe.pk, 'recipe_name': 'Pancakes'}
        self.serializer = RecipeSerializer(instance=self.recipe)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['recipe_id', 'recipe_name'])

    def test_data_matches_serializer_data(self):
        data = self.serializer.data
        for key in self.serializer_data:
            self.assertEqual(data[key], self.serializer_data[key])

class TestRecipePage(TestCase):

    def test_recipe_page(self):
        client = Client()
        response = client.get('/recipe/')
        self.assertEqual(response.status_code, 200)

class RecipesListViewTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        Recipe.objects.create(recipe_name="Lasagna") 
        Recipe.objects.create(recipe_name="Spaghetti")

    def test_get_all_recipes(self):
        """ Test to get details of all recipes """
        response = self.client.get("/api/recipe/getrecipelist/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
  
    def test_get_no_recipes(self):
        """ Test to check behaviour when no recipes are available """
        Recipe.objects.all().delete()
        response = self.client.get("/api/recipe/getrecipelist/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

class RecipeIngredientViewTests(TestCase):
  
    def setUp(self):
        self.client = APIClient()
        self.ingredient = RecipeIngredient.objects.create(name="Salt")
        self.url = f'/api/recipe/getingredient/{self.ingredient.pk}'

    def test_get_valid_recipe_ingredients(self):
        """
        Test to verify that we can retrieve a single ingredient object.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"ingredient_id": self.ingredient.pk, "name":"Salt"})
    
    def test_get_invalid_recipe_ingredients(self):
      """
      Test to verify that a 404 HTTP response is returned for invalid recipe id
      """
      url = f'/api/recipe/getingredient/{100000}'
      response = self.client.get(url)
      self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class RecipeDetailViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.recipe = Recipe.objects.create(recipe_name='Pancakes')
        self.ingredient1 = RecipeIngredient.objects.create(name='flour')
        self.ingredient2 = RecipeIngredient.objects.create(name='water')
        self.detail1 = RecipeDetail.objects.create(ingredient=self.ingredient1,
                                                    recipe=self.recipe,
                                                    quantity=500,
                                                    unit='g')
        self.detail2 = RecipeDetail.objects.create(ingredient=self.ingredient2,
                                                    recipe=self.recipe,
                                                    quantity=300,
                                                    unit='g',)             

    def test_get_single_recipe_detail(self):
        response = self.client.get(f'/api/recipe/getdetail/{self.detail1.detail_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['recipe']['recipe_id'], self.recipe.recipe_id)
        self.assertEqual(response.data['recipe']['recipe_name'], self.recipe.recipe_name)
        self.assertEqual(response.data['quantity'], self.detail1.quantity)
        self.assertEqual(response.data['unit'], self.detail1.unit)
        self.assertEqual(response.data['ingredient']['ingredient_id'], self.ingredient1.ingredient_id)
        self.assertEqual(response.data['ingredient']['name'], self.ingredient1.name)

    def test_get_nonexistent_recipe_detail(self):
        response = self.client.get(f'/api/recipe/getdetail/{100000}')
        self.assertEqual(response.status_code, 404)

class RecipeInfoViewTestCase(TestCase):
    """Test module for GET and DELETE methods of RecipeInfoView"""

    def setUp(self):

        self.client = APIClient()
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
                                                    quantity=200,
                                                    unit='g')
        self.detail4 = RecipeDetail.objects.create(ingredient=self.ingredient2,
                                                    recipe=self.recipe2,
                                                    quantity=100,
                                                    unit='g',)   
    
    def test_get_valid_recipe(self):
        response = self.client.get(f'/api/recipe/getrecipeinfo/{self.recipe1.recipe_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['recipe_id'],self.recipe1.recipe_id)
        self.assertEqual(response.data['recipe_name'],self.recipe1.recipe_name)

    def test_get_invalid_recipe(self):
        response = self.client.get(f'/api/recipe/getrecipeinfo/{100000}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_valid_recipe(self):
        response = self.client.delete(f'/api/recipe/getrecipeinfo/{self.recipe1.recipe_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_invalid_recipe(self):
        response = self.client.delete(f'/api/recipe/getrecipeinfo/{100000}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  


class RecipeDetailsListViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.recipe1 = Recipe.objects.create(recipe_name='Pancakes1')
        self.ingredient1 = RecipeIngredient.objects.create(name='flour')
        self.ingredient2 = RecipeIngredient.objects.create(name='water')
        self.ingredient3 = RecipeIngredient.objects.create(name='salt')

        self.detail1 = RecipeDetail.objects.create(ingredient=self.ingredient1,
                                                    recipe=self.recipe1,
                                                    quantity=500,
                                                    unit='g')
        self.detail2 = RecipeDetail.objects.create(ingredient=self.ingredient2,
                                                    recipe=self.recipe1,
                                                    quantity=300,
                                                    unit='g',)
        
        self.data = [
                        {
                            "detail_id": self.detail1.detail_id,
                            "quantity": self.detail1.quantity,
                            "unit": self.detail1.unit,
                            "recipe": {
                                "recipe_id": self.recipe1.recipe_id,
                                "recipe_name": self.recipe1.recipe_name
                            },
                            "ingredient": {
                                "ingredient_id": self.ingredient1.ingredient_id,
                                "name": self.ingredient1.name
                            }
                        },
                        {
                            "detail_id": self.detail2.detail_id,
                            "quantity": self.detail2.quantity,
                            "unit": self.detail2.unit,
                            "recipe": {
                                "recipe_id": self.recipe1.recipe_id,
                                "recipe_name": self.recipe1.recipe_name
                            },
                            "ingredient": {
                                "ingredient_id": self.ingredient2.ingredient_id,
                                "name": self.ingredient2.name
                            }
                        }
                    ]

        self.updatedata = [
                        {
                            "detail_id": self.detail1.detail_id,
                            "quantity": 900,
                            "unit": 'oz',
                            "ingredient": {
                                "name": self.ingredient1.name
                            }
                        },
                        {
                            "detail_id": self.detail2.detail_id,
                            "quantity": 100,
                            "unit": 'kg',
                            "ingredient": {
                                "name": self.ingredient2.name
                            }
                        }
                    ]
        self.newdata = [
                        {
                            "quantity": 200,
                            "unit": 'oz',
                            "ingredient": {
                                "name": self.ingredient1.name
                            }
                        },
                        {
                            "quantity": 100,
                            "unit": 'kg',
                            "ingredient": {
                                "name": self.ingredient2.name
                            }
                        },
                        {
                            "quantity": 300,
                            "unit": 'g',
                            "ingredient": {
                                "name": self.ingredient2.name
                            }
                        }
                    ]

    # Test GET request
    def test_get_recipe_details(self):
        response = self.client.get(f'/api/recipe/getrecipedetails/{self.recipe1.recipe_id}')

        # Check if status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data,self.data)

    # Test incorrect GET request
    def test_get_recipe_details_wrong_id(self):
        response = self.client.get(f'/api/recipe/getrecipedetails/{10000}')

        # Check if status code is 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Test PUT request
    def test_update_recipe_origin_details(self):
        params = {'recipe_id':self.recipe1.recipe_id,'details':self.updatedata}
        response = self.client.put('/api/recipe/recipedetails/',data = params,format='json')
        # Check if status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Test POST request
    def test_create_recipe_details(self):
        params = {'recipe_name':'Sale Cake','details':self.newdata}
        response = self.client.post('/api/recipe/recipedetails/',data = params,format='json')
        # Check if status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class RecipeDetailCheckViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # New Recipe
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
                                                    quantity=300,
                                                    unit='g')
        self.detail4 = RecipeDetail.objects.create(ingredient=self.ingredient2,
                                                    recipe=self.recipe2,
                                                    quantity=200,
                                                    unit='g',)
        # Own Ingredient
        self.owningredient1 = OwnIngredient.objects.create(name='flour')
        self.owningredient2 = OwnIngredient.objects.create(name='water')
        self.oidetail1 = OwnIngredientDetail.objects.create(ingredient=self.owningredient1,quantity=350,quantity_unit='g',expiry_date='2026-03-01')
        self.oidetail2 = OwnIngredientDetail.objects.create(ingredient=self.owningredient2,quantity=210,quantity_unit='g',expiry_date='2026-03-01')

    # Test GET request
    def test_get_recipe_details_enough(self):
        response = self.client.get(f'/api/recipe/recipecheck/{self.recipe2.recipe_id}')
        output_data = {
            'recipe_name': self.recipe2.recipe_name,
            'all_enough': True,
            'details': [
                    {
                    'ingredient_name': self.ingredient1.name,
                    'origin_quantity': 350,
                    'unit': self.oidetail1.quantity_unit,
                    'after_quantity': 50,
                    'enough': True
                    },{
                    'ingredient_name': self.ingredient2.name,
                    'origin_quantity': 210,
                    'unit': self.oidetail1.quantity_unit,
                    'after_quantity': 10,
                    'enough': True
                    }
            ]
        }
        # Check if status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, output_data)

    # Test GET request
    def test_get_recipe_details_not_enough(self):
        response = self.client.get(f'/api/recipe/recipecheck/{self.recipe1.recipe_id}')
        output_data = {
            'recipe_name': self.recipe1.recipe_name,
            'all_enough': False,
            'details': [
                    {
                    'ingredient_name': self.ingredient1.name,
                    'origin_quantity': 350,
                    'unit': self.oidetail1.quantity_unit,
                    'after_quantity': -150,
                    'enough': False
                    },{
                    'ingredient_name': self.ingredient2.name,
                    'origin_quantity': 210,
                    'unit': self.oidetail1.quantity_unit,
                    'after_quantity': -90,
                    'enough': False
                    }
            ]
        }
        # Check if status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, output_data)
    
    def test_use_recipe(self):
        params = {'recipe_id':self.recipe2.recipe_id}
        response = self.client.put('/api/recipe/recipeuse/',data = params,format='json')
        # Check if status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_oi_detail1_quantity = OwnIngredientDetail.objects.get(detail_id = self.oidetail1.detail_id).quantity
        new_oi_detail2_quantity = OwnIngredientDetail.objects.get(detail_id = self.oidetail2.detail_id).quantity
        self.assertEqual(new_oi_detail1_quantity, 50)
        self.assertEqual(new_oi_detail2_quantity, 10)