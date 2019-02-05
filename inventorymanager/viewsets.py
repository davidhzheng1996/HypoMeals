from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from django.contrib.auth.decorators import login_required



# APIView is specific for handling REST API requests. User need to Explicitly describe  
# the logic for post, get, delete, etc. If not described, action is not allowed. 
# ViewSet simplifies the API logic by providing common actions logic. 
# https://stackoverflow.com/questions/41379654/difference-between-apiview-class-and-viewsets-class/41380941
# https://stackoverflow.com/questions/32589087/django-rest-framework-difference-between-views-and-viewsets

class SkuViewSet(viewsets.ModelViewSet):
    queryset = Sku.objects.all()
    serializer_class = SkuSerializer
    filter_backends = (filters.SearchFilter, )
    # notice that we could also filter on foreign key's fields
    search_fields = ('sku_name', 'productline')

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # searching functionality
    # https://medium.com/quick-code/searchfilter-using-django-and-vue-js-215af82e12cd
    filter_backends = (filters.SearchFilter, )
    # notice that we could also filter on foreign key's fields
    search_fields = ('ingredient_name', 'description')

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class ManufactureGoalViewSet(viewsets.ModelViewSet):
    queryset = Manufacture_Goal.objects.all()
    serializer_class = ManufactureGoalSerializer

class ProductLineViewSet(viewsets.ModelViewSet):
    queryset = Product_Line.objects.all()
    serializer_class = ProductLineSerializer


# Begin Explicit APIs

# Skus within goal
@login_required(login_url='/accounts/login/')
@api_view(['POST'])
def manufacture_goals(request):
    if(request.method == 'POST'):
        try: 
            sku = Sku.objects.get(sku_name=request.data['goal_sku_name'])
            goal = Goal.objects.get(id=request.data['name'])
            # COUPLED WITH FRONT END MAY WANT TO REFACTOR
            request.data['sku'] = sku.id
            serializer = ManufactureGoalSerializer(data = request.data)
            if(serializer.is_valid()):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(status = status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/accounts/login/')
@api_view(['GET'])
def manufacture_goals_get(request,id,goalid):
    if(request.method == 'GET'):
        try: 
            goals = Manufacture_Goal.objects.filter(user = id, name=goalid)
            response = []
            for goal in goals:
                serializer = ManufactureGoalSerializer(goal)
                response.append(serializer.data)
            return Response(response,status = status.HTTP_200_OK)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/accounts/login/')
@api_view(['POST'])
def delete_manufacture_goal(request,specificgoal):
    if(request.method == 'POST'):
        try: 
            manufacture_goal = Manufacture_Goal.objects.filter(id = specificgoal)
            manufacture_goal.delete()
            return Response(status = status.HTTP_204_NO_CONTENT)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/accounts/login/')
@api_view(['POST'])
def update_manufacture_goal(request):
    if(request.method == 'POST'):
        try: 
            manufacture_goal = Manufacture_Goal.objects.get(id = request.data['id'])
            serializer = ManufactureGoalSerializer(manufacture_goal,{'desired_quantity':request.data['desired_quantity']},partial=True)
            if(serializer.is_valid()):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
            return Response(status = status.HTTP_400_BAD_REQUEST)
        except Exception as e: 
            print(e)
            return Response(status = status.HTTP_400_BAD_REQUEST)

# Singular Manufacturing Goal
@login_required(login_url='/accounts/login/')
@api_view(['GET','POST'])
def goal(request,id):
    if(request.method == 'GET'):
        try: 
            goals = Goal.objects.filter(user = id)
            response = []
            for goal in goals:
                serializer = GoalSerializer(goal)
                response.append(serializer.data)
            return Response(response,status = status.HTTP_200_OK)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)
    if(request.method == 'POST'):
        try: 
            serializer = GoalSerializer(data = request.data)
            if(serializer.is_valid()):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(status = status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/accounts/login/')
@api_view(['POST'])
def delete_goal(request,id,goalid):
    if(request.method == 'POST'):
        try: 
            goal = Goal.objects.filter(user = id, id=goalid)
            goal.delete()
            return Response(status = status.HTTP_204_NO_CONTENT)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/accounts/login/')
@api_view(['POST'])
def update_goal(request,id,goalid):
    if(request.method == 'POST'):
        try: 
            goal = Goal.objects.get(user = id, id=goalid)
            serializer = GoalSerializer(goal,{'goalname':request.data['goalname']},partial=True)
            if(serializer.is_valid()):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
            return Response(status = status.HTTP_400_BAD_REQUEST)
        except Exception as e: 
            print(e)
            return Response(status = status.HTTP_400_BAD_REQUEST)

