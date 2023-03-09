from django.test import TestCase,Client
from rest_framework.test import APIClient
from .models import OwnIngredient, OwnIngredientDetail
from .serializers import OICategoryCountSerializer, OIDetailSerializer
from .views import OwnIngredientCategoryView
from datetime import date, timedelta
from django.urls import reverse
from rest_framework import status



class ModelsTestCase(TestCase):

    def setUp(self):

        self.ingredient = OwnIngredient.objects.create(name="test ingredient")
        self.detail = OwnIngredientDetail.objects.create(
            ingredient=self.ingredient,
            quantity=1,
            quantity_unit="oz",
            expiry_date="2022-12-31"
        )

    def test_own_ingredient_creation(self):
        """Test that an OwnIngredient can be created"""
        ingredient = OwnIngredient.objects.create(name="new ingredient")
        self.assertEqual(ingredient.name, "new ingredient")

    def test_own_ingredient_detail_creation(self):
        """Test that an OwnIngredientDetail can be created"""
        detail = OwnIngredientDetail.objects.create(
            ingredient=self.ingredient,
            quantity=2,
            quantity_unit="g",
            expiry_date="2022-06-30"
        )
        self.assertEqual(detail.quantity, 2)
        self.assertEqual(detail.expiry_date, "2022-06-30")

    def test_own_ingredient_details_relation(self):
        """Test the reverse relation from OwnIngredient to its details"""
        details = self.ingredient.details.all()
        self.assertEqual(len(details), 1)
        self.assertEqual(details[0].quantity, 1)


class SerializersTestCases(TestCase):

    def setUp(self):

        self.own_ingredient = OwnIngredient.objects.create(name='Green pepper')

    def test_own_ingredient_creation(self):

        self.assertTrue(isinstance(self.own_ingredient, OwnIngredient))

    def test_own_ingredient_detail_creation(self):

        expiry_date = date.today()
        oi_detail1 = OwnIngredientDetail.objects.create(
            ingredient=self.own_ingredient,
            quantity=2,
            quantity_unit='g',
            expiry_date=expiry_date
        )
        self.assertTrue(isinstance(oi_detail1, OwnIngredientDetail))


        oi_detail2 = OwnIngredientDetail.objects.create(
            ingredient=self.own_ingredient,
            quantity=5,
            quantity_unit='oz',
            expiry_date=expiry_date
        )

        oicountserializer = OICategoryCountSerializer(self.own_ingredient)
        data = oicountserializer.data
        self.assertEqual(data['ingredient_id'],
                         self.own_ingredient.ingredient_id)
        self.assertEqual(data['name'], self.own_ingredient.name)
        # total_quantity = (2*1 + 5*28.35)
        self.assertEqual(data['quantity_and_unit']['total_quantity'], 143.75)
        self.assertEqual(data['nearst_expiry_date'], expiry_date)
        self.assertDictEqual(data['details'][0],
                             OIDetailSerializer(oi_detail1).data)
        self.assertDictEqual(data['details'][1],
                             OIDetailSerializer(oi_detail2).data)

    def test_oidetail_serializer(self):
 
        expiry_date = date.today()
        oi_detail = OwnIngredientDetail.objects.create(
            ingredient=self.own_ingredient,
            quantity=2,
            quantity_unit='g',
            expiry_date=expiry_date
        )

        oidetailserializer = OIDetailSerializer(oi_detail)
        data = oidetailserializer.data
        self.assertEqual(data['detail_id'], oi_detail.detail_id)
        self.assertEqual(data['ingredient']['name'], oi_detail.ingredient.name)
        self.assertEqual(data['quantity'], oi_detail.quantity)
        self.assertEqual(data['quantity_unit'], oi_detail.quantity_unit)
        self.assertEqual(data['expiry_date'], str(oi_detail.expiry_date))


class TestIngredientsPage(TestCase):

    def test_ingredients_page(self):
        client = Client()
        response = client.get('/ingredient/')
        self.assertEqual(response.status_code, 200)

# Test case to get statistics about own ingredients categories (if any)


class TestOwnIngredientCategoryView(TestCase):

    def setUp(self):
        self.client = APIClient()
        expiry_date = date.today()
        oi1 = OwnIngredient.objects.create(name='Milk')
        oi2 = OwnIngredient.objects.create(name='Sugar')
        oi1_detail1 = OwnIngredientDetail.objects.create(
            ingredient=oi1,
            quantity=2,
            quantity_unit='g',
            expiry_date=expiry_date + timedelta(days=10)
        )
        oi1_detail2 = OwnIngredientDetail.objects.create(
            ingredient=oi1,
            quantity=10,
            quantity_unit='lbs',
            expiry_date=expiry_date + timedelta(days=5)
        )
        oi2_detail1 = OwnIngredientDetail.objects.create(
            ingredient=oi2,
            quantity=5,
            quantity_unit='oz',
            expiry_date=expiry_date + timedelta(days=10)
        )

    def test_own_ingredient_category_view(self):

        response = self.client.get('/api/oi/getcategorylist/')
        expiry_date = date.today()
        actual_output = response.json()
        expected_output = [
            {
                'ingredient_id': 1,
                'name': 'Milk',
                'quantity_and_unit':
                {
                    "total_quantity": 4.5379,
                    "total_quantity_unit": 'kg'
                },
                "nearst_expiry_date": str(expiry_date + timedelta(days=5)),
                "details": [{
                    "detail_id": 1,
                    "ingredient": {
                        "ingredient_id": 1,
                        "name": "Milk"
                    },
                    "quantity": 2,
                    "quantity_unit": "g",
                    "expiry_date": str(expiry_date + timedelta(days=10))
                },
                    {
                    "detail_id": 2,
                    "ingredient": {
                        "ingredient_id": 1,
                        "name": "Milk"
                    },
                    "quantity": 10,
                    "quantity_unit": "lbs",
                    "expiry_date": str(expiry_date + timedelta(days=5))
                }]
            },
            {
                'ingredient_id': 2,
                'name': 'Sugar',
                'quantity_and_unit':
                {
                    "total_quantity": 141.75,
                    "total_quantity_unit": 'g'
                },
                "nearst_expiry_date": str(expiry_date + timedelta(days=10)),
                "details": [{
                    "detail_id": 3,
                    "ingredient": {
                        "ingredient_id": 2,
                        "name": "Sugar"
                    },
                    "quantity": 5,
                    "quantity_unit": "oz",
                    "expiry_date": str(expiry_date + timedelta(days=10))
                }]
            }
        ]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(actual_output, expected_output)

    def tearDown(self):
        OwnIngredient.objects.all().delete()
        OwnIngredientDetail.objects.all().delete()


class OwnIngredientDetailsListViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.expiry_date = date.today()
        self.oi = OwnIngredient.objects.create(name='Milk')
        self.oi_detail = OwnIngredientDetail.objects.create(
            ingredient=self.oi,
            quantity=2,
            quantity_unit='g',
            expiry_date=self.expiry_date + timedelta(days=10)
        )

    def test_get_with_valid_ingredient_detail(self):

        response = self.client.get(f'/api/oi/getdetailslist/{self.oi.ingredient_id}')
        expected_output = [
            {
                'detail_id': 1,
                'ingredient': {
                    'name': 'Milk',
                    'ingredient_id': 1,
                },
                'quantity': 2,
                'quantity_unit': 'g',
                'expiry_date': str(self.expiry_date + timedelta(days=10)),
            }
        ]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_output)

    def test_get_with_invalid_ingredient_id(self):
        response = self.client.get(f'/api/oi/getdetailslist/{9999}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OwnIngredientDetailViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create object
        self.expiry_date = date.today()
        self.oi = OwnIngredient.objects.create(name='Milk')
        self.oi_detail = OwnIngredientDetail.objects.create(
            ingredient=self.oi,
            quantity=2,
            quantity_unit='g',
            expiry_date=self.expiry_date + timedelta(days=10)
        )

    def test_get_own_ingredient_detail(self):

        # Retrieve object using GET request
        response = self.client.get(f'/api/oi/detail/{self.oi_detail.detail_id}')
      
        # Check if response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if returned data matches with created object
        self.assertEqual(response.data['detail_id'], self.oi_detail.detail_id)
        self.assertEqual(response.data['ingredient']['ingredient_id'], self.oi_detail.ingredient.ingredient_id)
        self.assertEqual(response.data['ingredient']['name'], self.oi_detail.ingredient.name)
        self.assertEqual(response.data['quantity'],self.oi_detail.quantity)
        self.assertEqual(response.data['quantity_unit'], self.oi_detail.quantity_unit)
        self.assertEqual(response.data['expiry_date'], str(self.oi_detail.expiry_date))

    def test_create_own_ingredient_detail(self):
        
        # Define post data
        payload = {
            'name': 'Butter',
            'quantity': '200',
            'quantity_unit':'g',
            'expiry_date':'2026-03-01'
        }
        
        # Post data to API
        response = self.client.post(f'/api/oi/detail/',payload,format='json')
        
            
        # Check if status code is HTTP_201_CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check if data in response has required keys and values
        self.assertEqual(response.data['ingredient']['name'], payload['name'])
        self.assertEqual(response.data['quantity'], float(payload['quantity']) )

    def test_update_own_ingredient_detail(self):    

        payload = {
                "ingredient_id": self.oi_detail.ingredient.ingredient_id,
                "detail_id": self.oi_detail.detail_id,
                "quantity": 300,
                "quantity_unit": 'oz',
                "expiry_date": str(self.expiry_date + timedelta(days=5))
        }
        
        # Put data to API
        response = self.client.put(f'/api/oi/detail/{self.oi_detail.detail_id}',payload,format='json')
        # Check if status code is HTTP_200_OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if updated data matches with given payload
        self.assertEqual(response.data['detail_id'], self.oi_detail.detail_id)
        self.assertEqual(response.data['ingredient']['ingredient_id'], self.oi_detail.ingredient.ingredient_id)
        self.assertEqual(response.data['ingredient']['name'], self.oi_detail.ingredient.name)
        self.assertEqual(response.data['quantity'],300)
        self.assertEqual(response.data['quantity_unit'], 'oz')
        self.assertEqual(response.data['expiry_date'], str(self.expiry_date + timedelta(days=5)))

    def test_delete_own_ingredient_detail(self):
        # Create object
        expiry_date = date.today()
        oi1 = OwnIngredient.objects.create(name='Sugar')
        oi_detail1 = OwnIngredientDetail.objects.create(
            ingredient=oi1,
            quantity=2,
            quantity_unit='g',
            expiry_date=expiry_date + timedelta(days=10)
        )
        
        # Delete object using API
        response = self.client.delete(f'/api/oi/detail/{oi_detail1.detail_id}')
        
        # Check if status code is HTTP_204_NO_CONTENT
        self.assertEqual(response.status_code, status.HTTP_200_OK)
