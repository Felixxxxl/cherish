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
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from ingredient import views
# from ingredient.views import IngredientViewSet, IngredientDetailViewSet, ingredient_tree

urlpatterns = [
    path("admin/", admin.site.urls),

    path('home/',views.homePage,name='home'),
    path('', RedirectView.as_view(url='home/',permanent = True)),
    path('ingredients/',views.ingredientsPage,name='ingredients'),


    path('api/oi/getcategorylist/',views.OwnIngredientCategoryView.as_view()),
    path('api/oi/getdetailslist/<ingredient_id>',views.OwnIngredientDetailsListView.as_view()),
    path('api/oi/detail/<detail_id>',views.OwnIngredientDetailView.as_view()),
    path('api/oi/detail/',views.OwnIngredientDetailView.as_view()),
]
