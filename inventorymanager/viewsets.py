from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from django.contrib.auth.decorators import login_required
from django.db.models import Q



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
    # filter_backends = (filters.SearchFilter, )
    # # notice that we could also filter on foreign key's fields
    # search_fields = ('ingredient_name', 'description')

    # https://www.django-rest-framework.org/api-guide/filtering/#filtering-against-query-parameters
    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.query_params.get('search', None)
        if search_term:
            queryset = Ingredient.objects.filter(Q(ingredient_name__icontains=search_term) | Q(description__icontains=search_term))
            # obtain all skus whose name contain search_term
            # https://docs.djangoproject.com/en/2.1/topics/db/examples/many_to_one/
            ingr_ids = Sku_To_Ingredient.objects.filter(sku__sku_name__icontains=search_term).values('ig')
            queryset |= Ingredient.objects.filter(id__in=ingr_ids)
        return queryset

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class ManufactureGoalViewSet(viewsets.ModelViewSet):
    queryset = Manufacture_Goal.objects.all()
    serializer_class = ManufactureGoalSerializer
    # filter_backends = (filters.SearchFilter, )
    # # notice that we could also filter on foreign key's fields
    # search_fields = ('goal_sku_name')

class ProductLineViewSet(viewsets.ModelViewSet):
    queryset = Product_Line.objects.all()
    serializer_class = ProductLineSerializer

    def destroy(self, request, *args, **kwargs):
        productline = self.get_object()
        # If related skus exist, abandon deletion 
        if Sku.objects.filter(productline=productline.id).exists():
            error = 'Related SKUs exist. Fail to delete %s' % productline.product_line_name
            return Response(error, status = status.HTTP_400_BAD_REQUEST)
        productline.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Begin Explicit APIs
@login_required(login_url='/accounts/login/')
@api_view(['GET','POST'])
def skus_to_ingredient(request,ingredientid):
    if(request.method == 'GET'):
        try: 
            sku_to_ingredient = Sku_To_Ingredient.objects.filter(ig=ingredientid)
            ids= sku_to_ingredient.values_list("sku",flat=True)
            skus = Sku.objects.filter(id__in=ids)
            response = []
            for sku in skus:
                serializer = SkuSerializer(sku)
                response.append(serializer.data)
            return Response(response,status = status.HTTP_200_OK)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/accounts/login/')
@api_view(['GET','POST'])
def ingredients_to_sku(request,skuid):
    if(request.method == 'GET'):
        try: 
            ingredients_to_sku = Sku_To_Ingredient.objects.filter(sku=skuid)
            ids= ingredients_to_sku.values_list("ig",flat=True)
            ingredients = Ingredient.objects.filter(id__in=ids)
            response = []
            for ingredient in ingredients:
                serializer = IngredientSerializer(ingredient)
                for relation in ingredients_to_sku: 
                    if(relation.ig.id == ingredient.id):
                        data = serializer.data
                        data['quantity'] = relation.quantity
                        response.append(data)
            return Response(response,status = status.HTTP_200_OK)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)
    if(request.method == 'POST'):
        try: 
            sku = Sku.objects.get(id=skuid)
            ingredient = Ingredient.objects.get(ingredient_name=request.data['ingredient_name'])
            newrelation = {'sku':sku.id,'ig':ingredient.id,'quantity':request.data['quantity']}
            serializer = IngredientToSkuSerializer(data=newrelation)
            if(serializer.is_valid()):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/accounts/login/')
@api_view(['POST'])
def delete_ingredients_to_sku(request,sku,ig):
    try: 
        ingredient_to_sku = Sku_To_Ingredient.objects.get(sku = sku,ig=ig)
        ingredient_to_sku.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)
    except Exception as e: 
        return Response(status = status.HTTP_400_BAD_REQUEST)


@login_required(login_url='/accounts/login/')
@api_view(['POST'])
def update_ingredients_to_sku(request,sku,ig):
    if(request.method == 'POST'):
        try: 
            relation = Sku_To_Ingredient.objects.get(sku = sku, ig=ig)
            serializer = IngredientToSkuSerializer(relation,{'quantity':request.data['quantity']},partial=True)
            if(serializer.is_valid()):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
            return Response(status = status.HTTP_400_BAD_REQUEST)
        except Exception as e: 
            print(e)
            return Response(status = status.HTTP_400_BAD_REQUEST)


@login_required(login_url='/accounts/login/')
@api_view(['POST'])
def manufacture_goals(request):
    if(request.method == 'POST'):
        try: 
            sku = Sku.objects.get(sku_name=request.data['goal_sku_name'])
            print(request.data['name'])
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

# SKUs within manufacture goal
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

# @login_required(login_url='/accounts/login/')
# @api_view(['GET'])
# def search_manufacture_goal(request,id,goalid):
#     if(request.method == 'GET'):
#         try: 
#             goals = Manufacture_Goal.objects.filter(user = id, name=goalid)
#             response = []
#             for goal in goals:
#                 serializer = ManufactureGoalSerializer(goal)
#                 response.append(serializer.data)
#             filter_backends = (filters.SearchFilter, )
#                  # notice that we could also filter on foreign key's fields
#             search_fields = ('ingredient_name', 'description')
#             return Response(response,status = status.HTTP_200_OK)
#         except Exception as e: 
#             return Response(status = status.HTTP_400_BAD_REQUEST)

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


