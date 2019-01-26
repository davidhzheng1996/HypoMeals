from rest_framework import viewsets
from rest_framework import parsers
from rest_framework import response
from rest_framework import status
from .models import *
from .serializers import *


class SkuViewSet(viewsets.ModelViewSet):
    queryset = Sku.objects.all()
    serializer_class = SkuSerializer

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    # Set up file upload rest api endpoint
    # https://www.trell.se/blog/file-uploads-json-apis-django-rest-framework/
    @decorators.action(
        detail=True,
        methods=['POST'],
        serializer_class=IngredientSerializer,
        # available parsers: https://www.django-rest-framework.org/api-guide/parsers/ 
        parser_classes=[parsers.FormParser, parsers.MultiPartParser],
    )
    def csv(self, request, pk):
        obj = self.get_object()
        serializer = self.serializer_class(obj, data=request.data,
                                           partial=True)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status.HTTP_201_CREATED)
        return response.Response(serializer.errors,
                                 status.HTTP_400_BAD_REQUEST)


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class ManufactureGoalViewSet(viewsets.ModelViewSet):
    queryset = Manufacture_Goal.objects.all()
    serializer_class = ManufactureGoalSerializer
