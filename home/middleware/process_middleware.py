from django.db import transaction
from datetime import date
from ingredient.models import OwnIngredientDetail
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

        expired_records = OwnIngredientDetail.objects.filter(expiry_date__lt=date.today())

        for record in expired_records:
                log_record = IngredientStatusLog.objects.create(
                    ingredient=record.ingredient,
                    quantity=record.quantity * UNIT_TRANS_DICT[record.quantity_unit],
                    date=record.expiry_date)
                record.delete()

        return response

