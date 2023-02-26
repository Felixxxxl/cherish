from django.db import models

# Create your models here.

class Recipe(models.Model):
    recipe_id = models.AutoField(primary_key=True)
    recipe_name = models.CharField(max_length=64)

    # def __str__(self):
    #     return 'Recipe'
    
class RecipeIngredient(models.Model):
    ingredient_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)

    # def __str__(self):
    #     return 'RecipeIngredient'
    
class RecipeDetail(models.Model):
    detail_id = models.AutoField(primary_key=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="details")
    ingredient = models.ForeignKey(RecipeIngredient, on_delete=models.CASCADE,related_name="ingredient")
    quantity = models.FloatField()
    unit = models.CharField(max_length=32)

    # def __str__(self):
    #     return 'RecipeDetail'
