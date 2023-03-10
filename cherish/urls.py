"""cherish URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from rest_framework.documentation import include_docs_urls
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from ingredient import views as ingredientView
from home import views as homeView
from recipe import views as recipeView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('home/',homeView.homepage,name='home'),
    path('', RedirectView.as_view(url='home/',permanent = True)),
    path('ingredient/',ingredientView.ingredientspage,name='ingredient'),
    path('recipe/',recipeView.recipepage,name='recipe'),
    path('log/',homeView.logpage,name='log'),

    path('api/oi/getcategorylist/',ingredientView.OwnIngredientCategoryView.as_view()),
    path('api/oi/getdetailslist/<ingredient_id>',ingredientView.OwnIngredientDetailsListView.as_view()),
    path('api/oi/detail/<detail_id>',ingredientView.OwnIngredientDetailView.as_view()),
    path('api/oi/detail/',ingredientView.OwnIngredientDetailView.as_view()),

    path('api/recipe/getrecipelist/',recipeView.RecipesListView.as_view()),
    path('api/recipe/getingredient/<ingredient_id>',recipeView.RecipeIngredientView.as_view()),
    path('api/recipe/getdetail/<detail_id>',recipeView.RecipeDetailView.as_view()),
    path('api/recipe/getrecipedetails/<recipe_id>',recipeView.RecipeDetailsListView.as_view()),
    path('api/recipe/getrecipeinfo/<recipe_id>',recipeView.RecipeInfoView.as_view()),
    path('api/recipe/recipedetails/',recipeView.RecipeDetailsListView.as_view()),

    path('api/recipe/recipecheck/<recipe_id>',recipeView.RecipeDetailCheckView.as_view()),
    path('api/recipe/recipeuse/',recipeView.RecipeDetailCheckView.as_view()),

    path('api/home/recommended/',homeView.RecommendRecipesView.as_view()),
    path('api/home/wastelog/',homeView.WastingLogView.as_view()),
    path('api/home/wastelogchart/',homeView.WastingLogChartView.as_view()),

    path('docs/', include_docs_urls(title='API docs')),

]
