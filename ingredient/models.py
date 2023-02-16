from django.db import models

# Create your models here.

class OwnIngredients(models.Model):

    unit_choices = [
        ('kilogram', 'Kilogram'),
        ('gram', 'Gram'),
        ('ounce', 'Ounce'),
        ('pound', 'Pound')
    ]
    type = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    quantity = models.FloatField()
    unit = models.CharField(max_length=12, choices=unit_choices) 
    expiration_date = models.DateField()
    
    class Meta:
        db_table = 'own_ingredients_info'
        verbose_name = "own_ingredients"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
    
