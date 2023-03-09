from django.db import transaction
from datetime import date
from ingredient.models import OwnIngredientDetail,OwnIngredient
from home.models import IngredientStatusLog

UNIT_TRANS_DICT = {
    'g': 1,
    'kg':1000,
    'oz':28.35,
    'lbs':453.59
}


class ExpiredProcessHnadler:
    def __init__(self,get_response):
        self.get_response = get_response

    def __call__(self,request):
        response = self.get_response(request)
        
        # Filter all the ingredient items whose expiration is over today's date.
        expired_records = OwnIngredientDetail.objects.filter(expiry_date__lt=date.today())
        with transaction.atomic():
            for record in expired_records:
                    # Create ingredient status logs for every expired record before deleting
                    log_record = IngredientStatusLog.objects.create(
                        ingredient_name=record.ingredient.name,
                        quantity=record.quantity * UNIT_TRANS_DICT[record.quantity_unit],
                        date=record.expiry_date)

                    # Check if there are other details for this ingredient
                    details = OwnIngredientDetail.objects.filter(ingredient__name = record.ingredient.name)
                     # Delete the expired detail record after logging data
                    record.delete()
                    
                    # If there are no more details for this ingredient, remove the whole ingredient category too
                    if not details.exists():
                        category = OwnIngredient.objects.get(name = record.ingredient.name)
                        category.delete()
                
        return response

