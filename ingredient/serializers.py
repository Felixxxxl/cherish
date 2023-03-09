from rest_framework import serializers
from .models import OwnIngredient, OwnIngredientDetail
from datetime import datetime
from django.db.models import Min

# A dictionary that maps units to their corresponding gram weight
UNIT_TRANS_DICT = {'g': 1, 'kg': 1000, 'oz': 28.35, 'lbs': 453.59}


class OICategorySerializer(serializers.Serializer):
    """
    Serializer class to represent the OwnIngredient model instance.

    """
    class Meta:
        model = OwnIngredient
        fields = '__all__'


class OICategoryCountSerializer(serializers.Serializer):
    """ 
    Serializer class to represent the information of each OwnIngredient.

    """
    ingredient_id = serializers.IntegerField()
    name = serializers.CharField()
    quantity_and_unit = serializers.SerializerMethodField(
        method_name='get_quantity_and_unit')
    nearst_expiry_date = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()

    def get_details(self, obj):
        """ 
    
        Method to get the serialization of OwnIngredient details

        params:
        obj: OwnIngredient object

        return:
        The serialization of ingredient details

        """
        details = obj.details.all()
        serialized_details = OIDetailSerializer(details, many=True).data
        return serialized_details

    def get_nearst_expiry_date(self, obj):
        """ 
    
        Method to get the nearest expiration date of an ingredient

        params:
        obj: OwnIngredient object

        return:
        The nearst expiration date of an ingredient

        """
        min_expiry_date = obj.details.aggregate(
            Min('expiry_date'))['expiry_date__min']
        return min_expiry_date

    def get_quantity_and_unit(self, obj):
        """ 
    
        Method to get the total amount and unit of ingredients

        params:
        obj: OwnIngredient object

        return:
        dict:{
            'total_quantity': Total amount of own ingredient,
            'total_quantity_unit': The unit of the total amount of own ingredient
            }

        """
        total_quantity_gram = sum(
            UNIT_TRANS_DICT.get(detail.quantity_unit) * detail.quantity
            for detail in obj.details.all())

        if total_quantity_gram >= 1000:
            return {
                'total_quantity': total_quantity_gram / 1000,
                'total_quantity_unit': 'kg'
            }
        else:
            return {
                'total_quantity': total_quantity_gram,
                'total_quantity_unit': 'g'
            }

    class Meta:
        model = OwnIngredient
        fields = '__all__'


class OIDetailSerializer(serializers.Serializer):
    """
    Serializer class to represent the OwnIngredientDetail model instance.

    """
    # define fields for serialization and deserialization
    detail_id = serializers.IntegerField(read_only=True)
    # a nested serializer to serialize OwnIngredient object
    ingredient = OICategorySerializer(required=False)
    quantity = serializers.FloatField()
    quantity_unit = serializers.CharField()
    expiry_date = serializers.DateField()

    class Meta:
        model = OwnIngredientDetail
        fields = '__all__'

    def update(self, instance, validated_data):
        """
        Method to update the instance of OwnIngredientDetail model with validated data.

        params:
        instance: The object to be updated
        validated_data: The validated data.

        return:
        The updated instance of the model.
        """
        instance.quantity = validated_data.get("quantity")
        instance.quantity_unit = validated_data.get("quantity_unit")
        instance.expiry_date = validated_data.get("expiry_date")
        instance.save()
        return instance

    def create(self, validated_data):
        """
        Method to create an instance of OwnIngredientDetail model with validated data.

        params:
        validated_data: The validated data.

        return:
        The created instance of the model.
        """
        detail = OwnIngredientDetail.objects.create(
            ingredient=self.context['ingredient'], **validated_data)
        return detail