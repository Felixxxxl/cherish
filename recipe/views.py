import json
from django.shortcuts import render
from rest_framework.views import APIView


from rest_framework.response import Response
from rest_framework import status

from django.db import transaction

from django.db.models import F, Case, When, CharField
from ingredient.serializers import OICategoryCountSerializer
from ingredient.models import OwnIngredient, OwnIngredientDetail
from .serializers import RecipeSerializer, IngredientSerializers, RecipeDetailSerializer, RecipeDetailsListSerializer
from .models import Recipe, RecipeDetail, RecipeIngredient


# Create your views here.
UNIT_TRANS_DICT = {'g': 1, 'kg': 1000, 'oz': 28.35, 'lbs': 453.59}


def recipepage(request):
    """ 
    This function is used to render the recipe page
    """
    return render(request, 'recipe.html')


class RecipesListView(APIView):
    """ 

    A view class representing the list view of recipes.

    HTTP Methods:
    - GET: Retrieves all recipe objects.

    """
    def get(self, request, *args, **kwargs):
        """
        Function to handle GET method for listing all the Recipe objects

        params:
        - request: The request object

        return:
        A serialized data of Recipe objects in JSON response
        """
        recipes = Recipe.objects.all()
        json_data = RecipeSerializer(recipes, many=True).data
        return Response(json_data)


class RecipeIngredientView(APIView):
    """ 
      A view class to get an individual recipe ingredient object based on its unique id.

      HTTP Methods:
      - GET: Retrieves a single recipe object for given recipe id.

    """
    def get(self, request, *args, **kwargs):
        """
        Function to handle GET method for retrieving a single recipe ingredient object based on its id.

        params:
        - request: The request object

        return:
        An HTTP Response object containing the JSON representation of the requested recipe object if found. Otherwise, returns a 404 HTTP response.
        """
        # Get the recipe id from the URL parameters.
        ingredient_id = kwargs.get('ingredient_id')
        try:
            # Try to fetch the requested recipe object using its unique id.
            ingredient = RecipeIngredient.objects.get(
                ingredient_id=ingredient_id)
        except RecipeIngredient.DoesNotExist:
            # Return 404 HTTP response if requested recipe object is not found.
            return Response(status = status.HTTP_404_NOT_FOUND)
        # If required recipe object is found, get the JSON representation using IngredientSerializers and return it as an HTTP response.
        json_data = IngredientSerializers(ingredient).data
        return Response(json_data)


class RecipeDetailView(APIView):
    """ 
      A view class to get an individual recipe detail based on its unique id.

      HTTP Methods:
      - GET: Retrieves a single recipe detail object for given recipe detail id.
    """
    def get(self, request, *args, **kwargs):
        """
        Function to handle GET method for retrieving a single recipe detail object based on its id.

        params:
        - request: The request object

        return:
        An HTTP Response object containing the JSON representation of the requested recipe detail object if found. Otherwise, returns a 404 HTTP response.
        """
        detail_id = kwargs.get('detail_id')
        try:
            detail = RecipeDetail.objects.get(detail_id=detail_id)
        except RecipeDetail.DoesNotExist:
            return Response(status = status.HTTP_404_NOT_FOUND)
        json_data = RecipeDetailSerializer(detail).data
        return Response(json_data,status=status.HTTP_200_OK)


class RecipeInfoView(APIView):
    """ 
    A view class to get the recipe information.

    HTTP Methods:
    - GET: Retrieves an individual recipe object based on its unique id.
           This method is used to retrieve details of a recipe such as name, description, etc., along with an array in JSON format containing information regarding its ingredient and directions.
    - DELETE: Deletes an individual recipe object based on its unique id. 

    """

    def get(self, request, *args, **kwargs):
        """
        Function to handle GET method for retrieving an individual recipe object.

        params:
        - request: The request object

        return:
        An HTTP Response object containing the JSON representation of the requested recipe object if found. Otherwise, returns a 404 HTTP response.
        """
        recipe_id = kwargs.get('recipe_id')
        try:
            recipe = Recipe.objects.get(recipe_id=recipe_id)
        except Recipe.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        json_data = RecipeDetailsListSerializer(recipe).data
        return Response(json_data,status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """
        Function to handle DELETE method for deleting an individual recipe object.

        params:
        - request: The request object

        return:
        An HTTP Response object containing a success message once the recipe has been deleted. Otherwise, returns a 404 HTTP response.
        """
        recipe_id = kwargs.get("recipe_id")
        try:
            recipe = Recipe.objects.get(recipe_id=recipe_id)
        except Recipe.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        details = RecipeDetail.objects.filter(recipe=recipe)
        details.delete()
        recipe.delete()
        return Response(data={"success": True},status=status.HTTP_200_OK)


class RecipeDetailsListView(APIView):
    """
    A view class for retrieving,editing,creating a recipe object

    HTTP Methods:
        - GET: Retrieves a list of recipe detail for given recipe recipe id.
        - PUT: Update an individual recipe object.
        - POST: Create a new recipe object
    """

    def get(self, request, *args, **kwargs):
        """
        Function to handle GET HTTP requests to retrieve recipe details from the database based on the specified ID.

        params:
        - request: The request object

        return:
        An HTTP Response object containing the JSON representation of the requested recipe details object if found. Otherwise, returns a 404 HTTP response.
        """
        recipe_id = kwargs.get('recipe_id')
        try:
            recipe = Recipe.objects.get(recipe_id=recipe_id)
        except Recipe.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        details = RecipeDetail.objects.filter(recipe=recipe)
        if not details.exists():
            return Response(status = status.HTTP_404_NOT_FOUND)
        json_data = RecipeDetailSerializer(details, many=True).data
        return Response(json_data,status=status.HTTP_200_OK)

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        """
        Function to handle PUT HTTP requests to update a recipe object.

        params:
        - request: The request object

        return:
        An HTTP Response object containing a success message once the recipe has been deleted. Otherwise, returns a 404 HTTP response.
        """
        # get the recipe details from request
        details = request.data.get('details')
        recipe_id = request.data.get('recipe_id')

        # Savepoint for DB
        save_id = transaction.savepoint()

        # get the recipe object
        try:
            recipe = Recipe.objects.get(recipe_id=recipe_id)
        except Recipe.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        # get the recipe detail
        details_db = RecipeDetail.objects.filter(recipe=recipe)
        # Used to store details id that have not been deleted
        detail_id_list = []
        # Store the original details id of the recipe
        origin_detail_id_list = [detail.detail_id for detail in details_db]

        # loop through each recipe details
        for detail in details:
            # check if its a new row
            if detail.get('detail_id') == 'newRow':
                # check if quantity and name whether it is empty
                if detail.get('quantity') == '' or detail.get('name') == '':
                    continue

                # create new ingredient and get existing one
                ingredient, _ = RecipeIngredient.objects.get_or_create(
                    name=detail['ingredient']['name']
                    )
                # create recipe detail object
                detail = RecipeDetail.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    quantity=detail['quantity'],
                    unit=detail['unit'])

            else:
                detail_id = detail['detail_id']
                 # if quantity or ingredient is empty delete detail object
                if detail['quantity'] == '' or detail['quantity'] == 0 or detail['ingredient']['name'] == '':
                    detail = RecipeDetail.objects.get(detail_id=detail_id).delete()
                    continue
                
                detail_id_list.append(detail_id)
                # create new ingredient and get existing one
                ingredient, _ = RecipeIngredient.objects.get_or_create(
                    name=detail['ingredient']['name']
                    )
                # assign ID to the ingredient
                detail['ingredient']['ingredient_id'] = ingredient.ingredient_id
                try:
                    detail_db = RecipeDetail.objects.get(detail_id=detail_id)
                except RecipeDetail.DoesNotExist:
                    # rollback the db in case of failure
                    transaction.savepoint_rollback(save_id)
                    # if object does not exist inside DB then return HTTP status 404
                    return Response(status=status.HTTP_404_NOT_FOUND)
                # serialize detail and modify it
                ser_data = RecipeDetailSerializer(detail_db, data=detail)

                if ser_data.is_valid():
                    # save serialized detail
                    ser_data.save()
                else:
                    # rollback the db in case of failure
                    transaction.savepoint_rollback(save_id)
                    return Response(status=status.HTTP_404_NOT_FOUND)

        # loop through each origin id from details_db
        for origin_id in origin_detail_id_list:
            id_int = str(origin_id)
            if id_int not in detail_id_list:
                try:
                    # if object exist then do nothing
                    detail = RecipeDetail.objects.get(detail_id=id_int)
                except RecipeDetail.DoesNotExist:
                    # if object does not exist then do nothing
                    continue
                detail.delete()            
        #return Http response with success message
        return Response(data={'success': True},status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Function to handle POST HTTP requests to create a recipe object.

        params:
        - request: The request object

        return:
        An HTTP Response object containing an error message if encountered. Otherwise, returns a success message.
        """
        # Get the details and recipe name from the request data
        details = request.data.get('details')
        recipe_name = request.data.get('recipe_name')
        # Create a savepoint for the transaction in case of errors
        save_id = transaction.savepoint()

        try:
            # Create a new Recipe object with the given recipe name
            recipe = Recipe.objects.create(recipe_name=recipe_name)
        except Exception as e:
            # Return a not found response in case of error 
            
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Loop through each detail in the list of details
        for detail in details:
            # Check if the quantity or ingredient name is empty or the quantity is 0
            if detail.get('quantity') == '' or detail.get('ingredient').get('name') == '' or detail.get('quantity') == 0:
                # Skip this detail if it doesn't have a valid quantity and ingredient
                continue
            # Get the quantity, unit, and ingredient name from the detail
            quantity = detail['quantity']
            unit = detail['unit']
            ingredient_name = detail['ingredient']['name']
            # Try to get the RecipeIngredient with the given name and create it if it doesn't exist
            ingredient,_ = RecipeIngredient.objects.get_or_create(name=ingredient_name)

            try:
                # Create a new RecipeDetail object with the recipe, ingredient, quantity, and unit
                ingredient_detail = RecipeDetail.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    quantity=quantity,
                    unit=unit)
            except Exception as e:
                # Rollback the transaction in case of error and return a not found response
                transaction.savepoint_rollback(save_id)
                return Response(status=status.HTTP_404_NOT_FOUND)
        # Return a success response
        return Response(data={'success': True},status=status.HTTP_200_OK)


class RecipeDetailCheckView(APIView):
    """ 
      This view is used to check whether the recipe details selected by the user meet the own ingredient, 
        and when the user uses the recipe, the processing of the existing own ingredient

      HTTP Methods:
      - GET: Check whether the recipe details selected by the user meet the ingredients inventory and return the own ingredients after use
      - PUT: User uses the recipe, the processing of the existing own ingredient

    """

    def get(self, request, *args, **kwargs):
        """
            This method checks whether the details entered by user in recipe fulfill the requirement of the recipe or not. 

            :params: request: The request object
            :return: returns the response in the form of JSON object containing success message (along with detailed information about recipe's four components)or failure (if recipe component is missing)
            
        """
        # Get recipe id from the request arguments
        recipe_id = kwargs.get('recipe_id')

        # Check if recipe exists or not
        try:
            recipe = Recipe.objects.get(recipe_id=recipe_id)
        except Recipe.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Get details of each recipe
        details = RecipeDetail.objects.filter(recipe=recipe)

        # If no detail is found for the recipe then respond with 404 error
        if not details.exists():
            return Response(status = status.HTTP_404_NOT_FOUND)

        # Create a dictionary for storing response
        response = {
            'recipe_name': recipe.recipe_name,
            'all_enough': True,
            'details': []
        }

        # Iterate over each detail of the recipe 
        for detail in details:

            # Create a dictionary for storing detail of the recipe
            detail_dict = {
                'ingredient_name': '',
                'origin_quantity': '',
                'unit': '',
                'after_quantity': '',
                'enough': True
            }

            # Add ingredient name in the detail dictionary
            detail_dict['ingredient_name'] = detail.ingredient.name

            # Get units and quantities of recipe and own ingredients respectively
            recipe_unit = detail.unit
            recipe_quantity = detail.quantity

            try:
                # Whether the ingredients required in the recipe are in stock
                ingredient = OwnIngredient.objects.get(name=detail.ingredient.name)
                # serialize the ingredient instance
                count_detail = OICategoryCountSerializer(ingredient)
                # Get the quantity unit of the ingredient
                oi_unit = count_detail.data['quantity_and_unit']['total_quantity_unit']
                # Get the quantity of the ingredient and convert the unit to the unit of the recipe ingredient
                oi_quantity = count_detail.data['quantity_and_unit']['total_quantity'] * UNIT_TRANS_DICT[oi_unit] / UNIT_TRANS_DICT[recipe_unit]
            except OwnIngredient.DoesNotExist:
                # The recipe does not meet the requirements
                response['all_enough'] = False
                # The ingredient does not meet the requirements
                detail_dict['enough'] = False
                oi_quantity = 0

            # Calculate difference between required quantity and available quantity
            diff = oi_quantity - recipe_quantity

            if diff < 0:
                # The ingredient does not meet the requirements
                detail_dict['enough'] = False
                # The recipe does not meet the requirements
                response['all_enough'] = False

            # Add ingredient unit,ingredient original quantity,ingredient after quantity in the detail dictionary
            detail_dict['unit'] = recipe_unit
            detail_dict['origin_quantity'] = oi_quantity
            detail_dict['after_quantity'] = diff

            # Append detail dictionary to the response dictionary
            response['details'].append(detail_dict)

        # Return response as JSON object
        return Response(data=response,status=status.HTTP_200_OK)

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        """
            This method is used to update the user's own Ingredient model to reflect the usage for making the recipe
            
            :params: request: The request object
            :return: returns the status after completing the operation
            
        """
        # retrieves the recipe id from the request data
        recipe_id = request.data.get('recipe_id')
        # creates a savepoint in case anything goes wrong during the transaction
        save_id = transaction.savepoint()
        
        print(recipe_id)

        try:
            # retrieves the recipe object from the database using its ID
            recipe = Recipe.objects.get(recipe_id=recipe_id)
        except Recipe.DoesNotExist:
            # if recipe doesn't exist, rolls back the transaction and returns a 404 error response
            return Response(status=status.HTTP_404_NOT_FOUND)

        # retrieves all RecipeDetail objects associated with the recipe
        details = RecipeDetail.objects.filter(recipe=recipe) 

        if not details.exists():
            # if no details are found, rolls back the transaction and returns a 404 error response
            return Response(status = status.HTTP_404_NOT_FOUND)

        # iterates through each RecipeDetail object
        for detail in details:

            # retrieves the name of the ingredient associated with the RecipeDetail object
            ingredient_name = detail.ingredient.name

            try:
                # retrieves the OwnIngredient object associated with the same ingredient name
                ingredient = OwnIngredient.objects.get(name=ingredient_name)
            except OwnIngredient.DoesNotExist:
                # if OwnIngredient doesn't exist, rolls back the transaction and returns a 404 error response
                transaction.savepoint_rollback(save_id)
                return Response(status = status.HTTP_404_NOT_FOUND)

            try:
                # retrieves all OwnIngredientDetail objects associated with the OwnIngredient object and orders them by expiry date and quantity
                details_db = OwnIngredientDetail.objects.filter(ingredient=ingredient)
                details_db = details_db.annotate(normalized_quantity=Case(
                    When(quantity_unit='kg', then=F('quantity') * 1000),
                    When(quantity_unit='lbs', then=F('quantity') * 453.59),
                    When(quantity_unit='oz', then=F('quantity') * 28.35),
                    default=F('quantity'),
                    output_field=CharField())).order_by(
                        'expiry_date', 'normalized_quantity')
            except Exception as e:
                # if there's an exception retrieving OwnIngredientDetail objects, rolls back the transaction and returns a 404 error response
                transaction.savepoint_rollback(save_id)
                return Response(status = status.HTTP_404_NOT_FOUND)

            # calculates the amount of the current ingredient required for making the current recipe detail
            count_quantity = detail.quantity * UNIT_TRANS_DICT[detail.unit]
            try:
                # iterates through each OwnIngredientDetail object
                for detail_db in details_db:
                    # calculates the amount of the current OwnIngredientDetail object in the required unit
                    quantity = detail_db.quantity * UNIT_TRANS_DICT[detail_db.quantity_unit]
                    # if the amount is greater than the amount required for making the current recipe detail, subtracts the amount and updates the OwnIngredientDetail object
                    if quantity > count_quantity:
                        detail_db.quantity = (quantity - count_quantity) / UNIT_TRANS_DICT[detail_db.quantity_unit]
                        detail_db.save()
                        break
                    # otherwise, deletes the OwnIngredientObject as it is used up by the recipe
                    else:
                        count_quantity = count_quantity - quantity
                        detail_db.delete()

            except Exception as e:
                # if there's an exception updating OwnIngredientDetail objects or deleting one of them, rolls back the transaction and returns a 404 error response
                transaction.savepoint_rollback(save_id)
                return Response(status = status.HTTP_404_NOT_FOUND)
        # if everything goes well, commits the transaction and returns a success message
        return Response(data={"success":True},status=status.HTTP_200_OK)
