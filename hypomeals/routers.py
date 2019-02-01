from rest_framework import routers
from inventorymanager.viewsets import *


# https://www.django-rest-framework.org/api-guide/routers/
# https://stackoverflow.com/questions/41379654/difference-between-apiview-class-and-viewsets-class/41380941
router = routers.DefaultRouter()

# map REST API url to corresponding ViewSet which provides a set of 
# common api request logic handling 
router.register(r'sku', SkuViewSet)
router.register(r'customer', CustomerViewSet)
router.register(r'ingredient', IngredientViewSet)
# router.register(r'manufacture_goal', ManufactureGoalViewSet) //replace with explicit
router.register(r'product_line', ProductLineViewSet)

