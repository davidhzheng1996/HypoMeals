from django.urls import path
from . import views, viewsets
from .views import IngredientImportView, IngredientExportView, SkuImportView, SkuExportView

# map url to views.view_class
urlpatterns = [
    path('', views.index, name='index'),
    # map /ingredient to ingredient.html
    path('ingredient',views.ingredient),
    # map /sku to sku.html
    path('sku',views.sku),
    path('manufacture_goal', views.manufacture_goal),
    path('product_line', views.product_line),
    # ingredient file upload endpoint
    # TODO how to integrate this with router's url patterns?
    path('api/ingredient_import/', IngredientImportView.as_view()),
    # ingredient file export endpoint 
    path('api/ingredient_export/', IngredientExportView.as_view()),
    path('api/manufacture_goal/', viewsets.manufacture_goals),
    path('api/manufacture_goal/<int:id>', viewsets.manufacture_goals_get),
    path('api/sku_import/', SkuImportView.as_view()),
    # ingredient file export endpoint 
    path('api/sku_export/', SkuExportView.as_view())
]