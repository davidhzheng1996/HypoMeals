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
    path('product_line', views.product_line),
    path('goal',views.goal),
    path('goal/<int:goalid>',views.manufacture_goal),
    # ingredient file upload endpoint
    # TODO how to integrate this with router's url patterns?
    path('api/ingredient_import/', IngredientImportView.as_view()),
    # ingredient file export endpoint 
    path('api/ingredient_export/', IngredientExportView.as_view()),
    path('api/manufacture_goal/', viewsets.manufacture_goals),
    path('api/manufacture_goal/<int:id>/<int:goalid>', viewsets.manufacture_goals_get),
    path('api/delete_manufacture_goal/<int:specificgoal>',viewsets.delete_manufacture_goal),
    path('api/update_manufacture_goal/',viewsets.update_manufacture_goal),
    path('api/goal/<int:id>', viewsets.goal),
    path('api/delete_goal/<int:id>/<int:goalid>', viewsets.delete_goal),
    path('api/update_goal/<int:id>/<int:goalid>', viewsets.update_goal),
    path('api/sku_import/', SkuImportView.as_view()),
    # ingredient file export endpoint 
    path('api/sku_export/', SkuExportView.as_view())
]