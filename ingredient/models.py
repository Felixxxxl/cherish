from django.db import models

class OwnIngredient(models.Model):

    ingredient_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return 'OwnIngredient'

class OwnIngredientDetail(models.Model):
    
    detail_id = models.AutoField(primary_key=True)
    ingredient = models.ForeignKey(OwnIngredient, on_delete=models.CASCADE, related_name="details")
    quantity = models.FloatField()
    quantity_unit = models.CharField(max_length=16)
    expiry_date = models.DateField()

    def __str__(self):
        return 'OwnIngredientDetail'
    