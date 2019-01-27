from django.urls import path
from . import views
from .views import IngredientFileView

# map url to views.view_class
urlpatterns = [
    path('', views.index, name='index'),
    # map /ingredient to ingredient.html
    path('ingredient',views.ingredient),
    # map /sku to sku.html
    path('sku',views.sku),
    # ingredient file upload endpoint
    # TODO how to integrate this with router's url patterns?
    path('api/ingredient_file/', IngredientFileView.as_view()),
    path('manufacture_goal', views.manufacture_goal)
]