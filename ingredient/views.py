from .models import OwnIngredient, OwnIngredientDetail
from rest_framework import viewsets, status
from .serializers import OICategoryCountSerializer, OIDetailSerializer, OICategorySerializer
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response


def ingredientsPage(request):
    return render(request, 'ingredients.html')


class OwnIngredientCategoryView(APIView):
    """ 

    A view for retrieving statistics for all objects of OwnIngredient.

    HTTP Methods:
    - GET: Retrieves statistics for all OwnIngredient objects.

    """
    def get(self, request, *args, **kwargs):
        """  

        Handle HTTP GET requests to obtain statistical information of own ingredients

        params:
        - request: request object

        return:
        - Response: The serialized OwnIngredient objects as JSON.
        """

        # Fetch all own ingredients categories from the DB
        category = OwnIngredient.objects.all()
        # Use the serializer to calculate and convert the queryset of your own ingredients into JSON format
        json = OICategoryCountSerializer(category, many=True)
        return Response(json.data)


class OwnIngredientDetailsListView(APIView):
    """ 
    A view for retrieving details of an OwnIngredient object.

    HTTP Methods:
    - GET: Retrieves details for a given OwnIngredient object.

    """
    def get(self, request, *args, **kwargs):
        """  

        Handle HTTP GET requests to obtain details of own ingredient

        params:
        - request: request object
        - kwargs: The keyword arguments containing the ingredient_id.

        return:
        - Response: The serialized OwnIngredientDetail objects as JSON.

        """

        # Get the ingredient ID from the URL parameters.
        ingredient_id = kwargs.get("ingredient_id")

        try:
            # Attempt to retrieve the OwnIngredient object with the given ID.
            ingredient = OwnIngredient.objects.get(ingredient_id=ingredient_id)
        except OwnIngredient.DoesNotExist:
            # If the OwnIngredient object does not exist, return a 404 error.
            return Response(status = status.HTTP_404_NOT_FOUND)

        # Retrieve all OwnIngredientDetail objects related to the given OwnIngredient object.
        details = OwnIngredientDetail.objects.filter(ingredient=ingredient)
        # If there are no related OwnIngredientDetail objects, return a 404 error.
        if not details.exists():
            return Response(status = status.HTTP_404_NOT_FOUND)

        # Serialize the OwnIngredientDetail objects and return them as JSON.
        json_data = OIDetailSerializer(details, many=True).data
        return Response(json_data)


class OwnIngredientDetailView(APIView):
    """ 
    a API view for OwnIngredientDetail model.

    HTTP Methods:
    - GET: Retrieves a specific OwnIngredientDetail object by detail_id
    - POST: Creates a new OwnIngredientDetail object.
    - PUT: Updates a specific OwnIngredientDetail object by detail_id.
    - DELETE: Deletes a specific OwnIngredientDetail object by detail_id.

    """
    
    def get(self, request, *args, **kwargs):
        """
        Retrieves a specific OwnIngredientDetail object by detail_id.

        Parameters:
        - request: The request object.
        - kwargs: The keyword arguments containing the detail_id.

        Returns:
        - Response: The serialized OwnIngredientDetail object as JSON.
        """

        # Retrieves the detail_id from the keyword arguments passed to the function
        detail_id = kwargs.get("detail_id")
        # Get the OwnIngredientDetail object with the specified detail_id
        try:
            detail = OwnIngredientDetail.objects.get(detail_id=detail_id)
        except OwnIngredientDetail.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Serializes the retrieved object and converts it to JSON
        json_data = OIDetailSerializer(detail).data
        # Returns the JSON data in a Response object
        return Response(json_data)

    def put(self, request, *args, **kwargs):
        """
        Updates a specific OwnIngredientDetail object by detail_id.

        Parameters:
        - request: The request object.
        - kwargs: The keyword arguments containing the detail_id.

        Returns:
        - Response: The serialized updated OwnIngredientDetail object as JSON or error messages.
        """

        # Retrieves the data from the request
        data = request.data
        # Retrieves the `detail_id` from the URL parameters
        detail_id = kwargs.get("detail_id")
        # Get the OwnIngredientDetail object with the specified detail_id
        try:
            detail = OwnIngredientDetail.objects.get(detail_id=detail_id)
        except OwnIngredientDetail.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Serializes the retrieved detail object with the update data and checks if the serialization is valid
        ser_data = OIDetailSerializer(detail, data=data)
        if ser_data.is_valid():
            detail = ser_data.save()
            return Response(ser_data.data)
        else:
            # If the serialization isn't valid, returns an error message with an error status code
            return Response(ser_data.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        """
        Creates a new OwnIngredientDetail object.

        Parameters:
        - request: The request object.

        Returns:
        - Response: The serialized created OwnIngredientDetail object as JSON or error messages.
        """
        # Retrieves the data from the request
        data = request.data
        # Retrieves the `name` from the URL parameters
        name = data.get('name')

        try:
            # Tries to get an existing ingredient with the extracted name
            ingredient = OwnIngredient.objects.get(name=name)
        except OwnIngredient.DoesNotExist:
            # If no ingredient already exists, creates a new ingredient with the extracted name
            ingredient = OwnIngredient.objects.create(name=name)

        # Serializes the data using OIDetailSerializer to create a new OwnIngredientDetail instance and defines the "ingredient" field
        ser_data = OIDetailSerializer(data=data,
                                      context={'ingredient': ingredient})

        if ser_data.is_valid():
            # Saves the serialized data as a new OwnIngredientDetail object
            ser_data.save()
            # Returns the response containing the serialized data in JSON format
            return Response(ser_data.data)
        else:
            # Deletes any created ingredient due to validation failure and prints the error message
            ingredient.delete()
            print(ser_data.error_messages)
            # Returns with Http status 400 cause invalid data input detected
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """
        Deletes a specific OwnIngredientDetail object by detail_id.

        Parameters:
        - request: The request object.
        - kwargs: The keyword arguments containing the detail_id.

        Returns:
        - Response: HTTP 204 NO CONTENT if the ingredient has no more details, otherwise HTTP 202 ACCEPTED.
        """

        # Retrieve the detail_id from the keyword arguments
        detail_id = kwargs.get("detail_id")
        # Get the OwnIngredientDetail object with the specified detail_id
        try:
            detail = OwnIngredientDetail.objects.get(detail_id=detail_id)
        except OwnIngredientDetail.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        # Get the corresponding ingredient and delete the detail
        ingredient = detail.ingredient
        detail.delete()
        # Check if there are any remaining details for this ingredient
        details = OwnIngredientDetail.objects.filter(ingredient=ingredient)
        if not details.exists():
            # If there are no more details, delete the ingredient
            ingredient.delete()
        # If there are still other details, return HTTP 202
        return Response(data={"success": True})
