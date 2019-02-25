from django.urls import path
from . import views, viewsets
from .views import IngredientImportView, IngredientExportView, SkuImportView, SkuExportView, FormulaImportView, FormulaExportView, ProductLineImportView

# map url to views.view_class
urlpatterns = [
    path('', views.index, name='index'),
    # map /ingredient to ingredient.html
    path('ingredient',views.ingredient),
    path('netid',views.netid),
    # map /sku to sku.html
    path('sku',views.sku),
    path('formula',views.formula),
    path('product_line', views.product_line),
    path('manufacture_line', views.manufacture_line),
    path('goal',views.goal),
    path('goal/<int:goalid>',views.manufacture_goal),
    path('sku/<int:formulaid>',views.formula_to_sku),
    path('formula/<int:formulaid>',views.ingredients_to_formula),
    path('show_formula/<int:formulaid>',views.skus_to_formula),
    path('ingredient/<int:ingredientid>',views.skus_to_ingredients),
    path('scheduler',views.scheduler),
    path('calculate_goal/<int:goalid>',views.calculate_goal),
    # ingredient file upload endpoint
    # TODO how to integrate this with router's url patterns?
    path('api/ingredient_import/', IngredientImportView.as_view()),
    # ingredient file export endpoint 
    path('api/ingredient_export/', IngredientExportView.as_view()),
    path('api/calculate_goal/<int:goalid>',viewsets.calculate_goal),
    path('api/skus_to_ingredient/<int:ingredientid>',viewsets.skus_to_ingredient),
    path('api/netid',viewsets.netid_login),
    path('api/skus_to_formula/<int:formulaid>',viewsets.skus_to_formula),
    path('api/formula_to_sku/<int:formulaid>',viewsets.formula_to_sku),
    path('api/mls_to_sku/<int:skuid>',viewsets.mls_to_sku),
    path('api/add_ml_to_sku/<int:skuid>/<int:mlshortname>',viewsets.add_ml_to_sku),
    # path('api/calculate_goal/<int:id>/<int:goalid>',viewsets.calculate_ingredient),
    path('api/ingredients_to_sku/<int:skuid>',viewsets.ingredients_to_sku),
    path('api/delete_ingredients_to_sku/<int:sku>/<int:ig>',viewsets.delete_ingredients_to_sku),
    path('api/update_ingredients_to_sku/<int:sku>/<int:ig>',viewsets.update_ingredients_to_sku),
    path('api/ingredients_to_formula/<int:formulaid>',viewsets.ingredients_to_formula),
    path('api/delete_ingredients_to_formula/<int:formula>/<int:ig>',viewsets.delete_ingredients_to_formula),
    path('api/update_ingredients_to_formula/<int:formula>/<int:ig>',viewsets.update_ingredients_to_formula),
    path('api/manufacture_goal/', viewsets.manufacture_goals),
    path('api/manufacture_goal/<int:id>/<int:goalid>', viewsets.manufacture_goals_get),
    path('api/delete_manufacture_goal/<int:specificgoal>',viewsets.delete_manufacture_goal),
    path('api/update_manufacture_goal/',viewsets.update_manufacture_goal),
    path('api/goal/<int:id>', viewsets.goal),
    path('api/delete_goal/<int:id>/<int:goalid>', viewsets.delete_goal),
    path('api/update_goal/<int:id>/<int:goalid>', viewsets.update_goal),
    path('api/sku_import/', SkuImportView.as_view()),
    path('api/sku_export/', SkuExportView.as_view()),
    path('api/formula_import/', FormulaImportView.as_view()),
    path('api/formula_export/', FormulaExportView.as_view()),
    path('api/product_line_import/', ProductLineImportView.as_view()),
    path('api/active_manufacturing_lines/', viewsets.active_manufacturing_lines),
    path('api/bulk_match_manufacturing_lines/', viewsets.bulk_match_manufacturing_lines)
]