from rest_framework import routers
from inventorymanager.viewsets import *

# router maps rest api urls to correponding ViewSets 
router = routers.DefaultRouter()

# /sku now maps to SkuViewSet
router.register(r'sku', SkuViewSet)
router.register(r'customer', CustomerViewSet)
router.register(r'ingredient', IngredientViewSet)
router.register(r'manufacture_goal', ManufactureGoalViewSet)

