from django.test import TestCase
from ingredient.models import OwnIngredients

class TestOwnIngredientsModel(TestCase):

    def setUp(self):
        self.ingredient = OwnIngredients.objects.create(
            type = 'food',
            name = 'rice',
            amount = '0.6',
            unit = 'pound',
            expiration_date = '2025-06-01'
        )

    def test_owningredientsmodel(self):
        ingredient = OwnIngredients.objects.get(id = self.ingredient.id)
        self.assertEqual(ingredient.amount,0.6)