from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.serializers import serialize
from .models import *
from .serializers import *

# APIView is specific for handling REST API requests. User need to Explicitly describe  
# the logic for post, get, delete, etc. If not described, action is not allowed. 
# ViewSet simplifies the API logic by providing common actions logic. 
# https://stackoverflow.com/questions/41379654/difference-between-apiview-class-and-viewsets-class/41380941
# https://stackoverflow.com/questions/32589087/django-rest-framework-difference-between-views-and-viewsets

class SkuViewSet(viewsets.ModelViewSet):
    queryset = Sku.objects.all()
    serializer_class = SkuSerializer

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # searching functionality
    # https://medium.com/quick-code/searchfilter-using-django-and-vue-js-215af82e12cd
    # filter_backends = (filters.SearchFilter, )
    # # notice that we could also filter on foreign key's fields
    # search_fields = ('ingredient_name', 'description', 'comment')

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class ManufactureGoalViewSet(viewsets.ModelViewSet):
    queryset = Manufacture_Goal.objects.all()
    serializer_class = ManufactureGoalSerializer

class ProductLineViewSet(viewsets.ModelViewSet):
    queryset = Product_Line.objects.all()
    serializer_class = ProductLineSerializer

@api_view(['POST'])
def manufacture_goals(request):
    if(request.method == 'POST'):
        try: 
            sku = Sku.objects.get(sku_name=request.data['goal_sku_name'])
            # COUPLED WITH FRONT END MAY WANT TO REFACTOR
            request.data['sku'] = sku.id
            serializer = ManufactureGoalSerializer(data = request.data)
            if(serializer.is_valid()):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status = status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def manufacture_goals_get(request,id):
    if(request.method == 'GET'):
        try: 
            goals = Manufacture_Goal.objects.get(user = id)
            return Response(serialize.data,status = status.HTTP_200_SUCCESS)
        except Exception as e: 
            print(e)
