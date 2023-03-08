from django.db import models


class OwnIngredient(models.Model):
    """
    A model class representing an own ingredient.

    """
    # primary key for this model
    ingredient_id = models.AutoField(primary_key=True)
    # name of the ingredient, maximum length 64 characters, must be unique
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return 'OwnIngredient'


class OwnIngredientDetail(models.Model):
    """
    A model class representing details of an own ingredient.

    """
    # primary key for this model
    detail_id = models.AutoField(primary_key=True)
    # foreign key to the OwnIngredient model, on_delete means what to do when an ingredient is deleted,
    # CASCADE means to also delete all OwnIngredientDetails that reference it.
    # related_name creates a reverse relation from OwnIngredient to its details, which can be used to access
    # all details for a specific ingredient.
    ingredient = models.ForeignKey(OwnIngredient,
                                   on_delete=models.CASCADE,
                                   related_name="details")
    # quantity of the ingredient, stored as a float
    quantity = models.FloatField()
    # unit for the quantity of the ingredient, maximum length 16 characters
    quantity_unit = models.CharField(max_length=16)
    # expiry date for the ingredient, stored as a date field
    expiry_date = models.DateField()

    def __str__(self):
        return "OwnIngredientDetail"
