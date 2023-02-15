from django.test import TestCase
from ingredient.models import OwnIngredients
from ingredient.serializers import OwnIngredientsSerializers
from datetime import date


class TestOwnIngredientsModel(TestCase):

    def setUp(self):
        self.ingredient = OwnIngredients.objects.create(
            type = 'food',
            name = 'rice',
            amount = 0.6,
            unit = 'pound',
            expiration_date = '2025-06-01'
        )

    def test_owningredientsmodel(self):
        ingredient = OwnIngredients.objects.get(id = self.ingredient.id)
        self.assertEqual(ingredient.amount, 0.6)
        ingredient = OwnIngredients.objects.get(id = self.ingredient.id)
        self.assertEqual(ingredient.type,'food')
        ingredient = OwnIngredients.objects.get(id = self.ingredient.id)
        self.assertEqual(ingredient.name,'rice')
        ingredient = OwnIngredients.objects.get(id = self.ingredient.id)
        self.assertEqual(ingredient.unit,'pound')
        ingredient = OwnIngredients.objects.get(id = self.ingredient.id)
        self.assertEqual(ingredient.expiration_date,date(2025,6,1))


class TestOwnIngredientsSerializers(TestCase):
    def setUp(self):
        self.ingredient = OwnIngredients.objects.create(
            type = 'food',
            name = 'rice',
            amount = 0.6,
            unit = 'pound',
            expiration_date = '2025-06-01'
        )

        self.serializer = OwnIngredientsSerializers(instance=self.ingredient)

    def test_serializer_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(),['type','name','amount','unit','expiration_date'])

    def test_serializer_data_matches_instance_values(self):
        data = self.serializer.data
        self.assertEqual(data['type'], self.ingredient.type)
        self.assertEqual(data['name'], self.ingredient.name)
        self.assertEqual(data['amount'], self.ingredient.amount)
        self.assertEqual(data['unit'], self.ingredient.unit)
        self.assertEqual(data['expiration_date'], str(self.ingredient.expiration_date))
