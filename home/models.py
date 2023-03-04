from django.db import models
from ingredient.models import OwnIngredient


# Create your models here.
class IngredientStatusLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    ingredient = models.ForeignKey(OwnIngredient, on_delete=models.DO_NOTHING,related_name='log')
    quantity = models.FloatField()
    date = models.DateField()


        