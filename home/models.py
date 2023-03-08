from django.db import models
from ingredient.models import OwnIngredient


# Create your models here.
class IngredientStatusLog(models.Model):
    """ 
    A model class representing a ingredient waste log.

    """
    log_id = models.AutoField(primary_key=True)
    ingredient_name = models.CharField(max_length=64)
    quantity = models.FloatField()
    date = models.DateField()


        