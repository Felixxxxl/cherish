from django.db import models

# Create your models here.


class Recipe(models.Model):
    """ 
    A model class representing a recipe.

    """
    recipe_id = models.AutoField(primary_key=True)
    recipe_name = models.CharField(max_length=64)


class RecipeIngredient(models.Model):
    """ 
    A model class representing an ingredient.

    """
    ingredient_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)


class RecipeDetail(models.Model):
    """ 
    A model class representing the detail ingredient of recipe.

    """
    detail_id = models.AutoField(primary_key=True)
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name="details")
    ingredient = models.ForeignKey(RecipeIngredient,
                                   on_delete=models.CASCADE,
                                   related_name="ingredient")
    quantity = models.FloatField()
    unit = models.CharField(max_length=32)
