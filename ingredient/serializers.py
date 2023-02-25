from rest_framework import serializers
from .models import OwnIngredient, OwnIngredientDetail
from datetime import datetime

UNIT_TRANS_DICT = {
    'g': 1,
    'kg':1000,
    'oz':28.35,
    'lbs':453.59
}

class OICategorySerializer(serializers.Serializer):
    ingredient_id = serializers.IntegerField()
    name = serializers.CharField()

    class Meta:
        model = OwnIngredient
        fields = '__all__'

class OICategoryCountSerializer(serializers.Serializer):
    ingredient_id = serializers.IntegerField()
    name = serializers.CharField()
    quantity_and_unit = serializers.SerializerMethodField(method_name='get_quantity_and_unit')
    nearst_expiry_date = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()

    def get_details(self,obj):
        details = obj.details.all()
        serialized_details = OIDetailSerializer(details, many=True).data
        return serialized_details
    
    def get_nearst_expiry_date(self,obj):
        date_objs = [detail.expiry_date for detail in obj.details.all()]
        date_objs.sort()
        return date_objs[0]
    
    def get_quantity_and_unit(self,obj):
        total_quantity_gram = 0
        for detail in obj.details.all():
            quantity = UNIT_TRANS_DICT.get(detail.quantity_unit) * detail.quantity
            total_quantity_gram += quantity

        if total_quantity_gram >= 1000:
            
            return {'total_quantity':total_quantity_gram/1000,'total_quantity_unit':'kg'}
        else:
            return {'total_quantity':total_quantity_gram,'total_quantity_unit':'g'}
    
    class Meta:
        model = OwnIngredient
        fields = '__all__'

class OIDetailSerializer(serializers.Serializer):
    detail_id = serializers.IntegerField(read_only=True)
    ingredient = OICategorySerializer(required=False)
    quantity = serializers.FloatField()
    quantity_unit = serializers.CharField()
    expiry_date = serializers.DateField()

    class Meta:
        model = OwnIngredientDetail
        fields = '__all__'  

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get("quantity")
        instance.quantity_unit = validated_data.get("quantity_unit")
        instance.expiry_date = validated_data.get("expiry_date")
        instance.save()
        return instance
    
    def create(self, validated_data):
        detail = OwnIngredientDetail.objects.create(ingredient = self.context['ingredient'],**validated_data)
        return detail
