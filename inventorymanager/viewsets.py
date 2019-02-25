from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.middleware.csrf import CsrfViewMiddleware, get_token
from django.test import Client
from django.contrib.auth.models import User


import requests
import re

# APIView is specific for handling REST API requests. User need to Explicitly describe  
# the logic for post, get, delete, etc. If not described, action is not allowed. 
# ViewSet simplifies the API logic by providing common actions logic. 
# https://stackoverflow.com/questions/41379654/difference-between-apiview-class-and-viewsets-class/41380941
# https://stackoverflow.com/questions/32589087/django-rest-framework-difference-between-views-and-viewsets

class SkuViewSet(viewsets.ModelViewSet):
    queryset = Sku.objects.all()
    serializer_class = SkuSerializer

    # GET override
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        queryset = Sku.objects.all()
        serializer = self.get_serializer(queryset,many=True)
        # attach a cell of ml_short_names to skus
        for sku in serializer.data:
            ml_short_names = Sku_To_Ml_Shortname.objects.filter(sku=sku['id']).values_list("ml_short_name",flat=True)
            cell = ','.join(list(ml_short_names))
            sku['ml_short_names'] = '"%s"' % cell
        return Response(serializer.data)

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.query_params.get('search', None)
        if search_term:
            queryset = Sku.objects.filter(Q(sku_name__icontains=search_term) | Q(productline__product_line_name__icontains=search_term))
            # obtain all skus whose ingredient names include search_term
            sku_ids = Sku_To_Ingredient.objects.filter(ig__ingredient_name__icontains=search_term).values('sku')
            queryset |= Sku.objects.filter(id__in=sku_ids)
        return queryset

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    # https://www.django-rest-framework.org/api-guide/filtering/#filtering-against-query-parameters
    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.query_params.get('search', None)
        if search_term:
            queryset = Ingredient.objects.filter(Q(ingredient_name__icontains=search_term) | Q(description__icontains=search_term))
            # obtain all ingrs whose name contain search_term
            ingr_ids = Sku_To_Ingredient.objects.filter(sku__sku_name__icontains=search_term).values('ig')
            queryset |= Ingredient.objects.filter(id__in=ingr_ids)
        return queryset

class FormulaViewSet(viewsets.ModelViewSet):
    queryset = Formula.objects.all()
    serializer_class = FormulaSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class ManufactureGoalViewSet(viewsets.ModelViewSet):
    queryset = Manufacture_Goal.objects.all()
    serializer_class = ManufactureGoalSerializer
    # filter_backends = (filters.SearchFilter, )
    # # notice that we could also filter on foreign key's fields
    # search_fields = ('goal_sku_name')

class ManufactureLineViewSet(viewsets.ModelViewSet):
    queryset = Manufacture_line.objects.all()
    serializer_class = ManufactureLineSerializer

class ProductLineViewSet(viewsets.ModelViewSet):
    queryset = Product_Line.objects.all()
    serializer_class = ProductLineSerializer

    def destroy(self, request, *args, **kwargs):
        productline = self.get_object()
        # If related skus exist, abandon deletion 
        if Sku.objects.filter(productline=productline.product_line_name).exists():
            error = 'Related SKUs exist. Fail to delete %s' % productline.product_line_name
            return Response(error, status = status.HTTP_400_BAD_REQUEST)
        productline.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.query_params.get('search', None)
        if search_term:
            queryset = Product_Line.objects.filter(product_line_name__icontains=search_term)
        return queryset

# Begin Explicit APIs
@login_required(login_url='/accounts/login/')
@api_view(['POST'])
# return list of all manufacturing lines with status 
def active_manufacturing_lines(request):
    if(request.method=='POST'):
        try: 
            active_sku_ids = request.data
            # ml_short_name -> num_active_sku
            ml_active_skus_count = {}
            for sku_id in active_sku_ids:
                mls_to_formula = Sku_To_Ml_Shortname.objects.filter(sku=sku_id)
                ml_short_names= mls_to_formula.values_list("ml_short_name",flat=True) 
                for name in ml_short_names:
                    if name in ml_active_skus_count.keys():
                        ml_active_skus_count[name] += 1
                    else:
                        ml_active_skus_count[name] = 1
            response = []
            for ml in Manufacture_line.objects.all():
                serializer = ManufactureLineSerializer(ml)
                ml_data = serializer.data
                short_name = ml_data['ml_short_name']
                ml_data['all_active'] = False
                ml_data['part_active'] = False
                if short_name in ml_active_skus_count.keys():
                    if len(active_sku_ids) == ml_active_skus_count[short_name]:
                        ml_data['all_active'] = True
                    else:
                        ml_data['part_active'] = True
                response.append(ml_data)
            return Response(response,status = status.HTTP_200_OK)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)


@login_required(login_url='/accounts/login/')
@api_view(['POST'])
# return list of all manufacturing lines with status 
def bulk_match_manufacturing_lines(request):
    if(request.method=='POST'):
        try: 
            active_sku_ids = request.data['active_sku_ids']
            active_ml_short_names = request.data['active_ml_short_names']
            all_ml_short_names = Manufacture_line.objects.all().values_list("ml_short_name",flat=True)
            response = []
            for sku_id in active_sku_ids:
                for ml_short_name in all_ml_short_names:
                    if ml_short_name in active_ml_short_names:
                        if Sku_To_Ml_Shortname.objects.filter(sku=sku_id,ml_short_name=ml_short_name).exists():
                            continue
                        sku = Sku.objects.get(id=sku_id)
                        ml = Manufacture_line.objects.get(ml_short_name=ml_short_name)
                        newrelation = {'sku':sku.id,'ml_short_name':ml.ml_short_name}
                        serializer = ManufactureLineToSkuSerializer(data=newrelation)
                        if(serializer.is_valid()):
                            serializer.save()
                            response.append(serializer.data)
                        else:
                            return Response(status=status.HTTP_400_BAD_REQUEST)
                    # Also need to remove all relationship between active_skus and non_active_mls
                    else:
                        if Sku_To_Ml_Shortname.objects.filter(sku=sku_id,ml_short_name=ml_short_name).exists():
                            delete_relation = Sku_To_Ml_Shortname.objects.get(sku=sku_id,ml_short_name=ml_short_name)
                            delete_relation.delete()
            return Response(response,status = status.HTTP_200_OK)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)



@login_required(login_url='/accounts/login/')
@api_view(['GET'])
def calculate_goal(request,goalid):

    def unit_handling(package_size_unit, quantity_unit, float_quantity, float_package_size, desired_quantity, formula_scale_factor):
        mass = ['lb', 'pound', 'oz', 'ounce', 'ton', 'g', 'gram', 'kg', 'kilogram']
        volume = ['floz', 'fluidounce', 'pt', 'pint', 'qt', 'quart', 'gal', 'gallon', 'ml', 'milliliter', 'l', 'liter']
        count = ['ct', 'count']
        mass_dict = {}
        volume_dict = {}
        mass_dict['lb'] = 2.20
        mass_dict['pound'] = 2.20
        mass_dict['oz'] = 35.27
        mass_dict['ounce'] = 35.27
        mass_dict['ton'] = 0.0011
        mass_dict['g'] = 1000.00
        mass_dict['gram'] = 1000.00
        mass_dict['kg'] = 1.00
        mass_dict['kilogram'] = 1.00
        volume_dict['floz'] = 33.81
        volume_dict['fluidounce'] = 33.81
        volume_dict['pt'] = 2.11
        volume_dict['pint'] = 2.11
        volume_dict['qt'] = 1.06
        volume_dict['quart'] = 1.06
        volume_dict['gal'] = 0.26
        volume_dict['gallon'] = 0.26
        volume_dict['ml'] = 1000.00
        volume_dict['milliliter'] = 1000.00
        volume_dict['l'] = 1.00
        volume_dict['liter'] = 1.00

        num = float(desired_quantity)*formula_scale_factor

        if package_size_unit in count and quantity_unit in count:
            res = num*float_quantity
            return res
        elif package_size_unit in mass and quantity_unit in mass:
            mass_converted = (float_quantity/(mass_dict[quantity_unit]))*mass_dict[package_size_unit]
            print("converted mass"+str(mass_converted))
            res1 = num*mass_converted
            return res1
        elif package_size_unit in volume and quantity_unit in volume:
            volume_converted = (float_quantity/(volume_dict[quantity_unit]))*volume_dict[package_size_unit]
            res2 = num*volume_converted
            return res2

        return 0
        

    if(request.method=='GET'):
        try: 
            errors = []
            manufacture_goals = Manufacture_Goal.objects.filter(name = goalid)
            response = {}
            for goal in manufacture_goals:
                skuid = goal.sku.id
                sku = Sku.objects.get(id = skuid)
                formula = sku.formula
                ingredients = Formula_To_Ingredients.objects.filter(formula = formula)
                for ingredient in ingredients: 
                    temp = []
                    package_size = re.findall(r'\d*\.?\d+', ingredient.ig.package_size)
                    package_size_unit0 = re.sub(r'\d*\.?\d+', '', ingredient.ig.package_size)
                    package_size_unit = package_size_unit0.replace(' ', '').replace('.','').lower()
                    if(package_size_unit[len(package_size_unit)-1]=='s'):
                        package_size_unit = package_size_unit[:-1]
                    float_package_size = float(package_size[0]) # from ingredient's package size
                    ingredient_quantity = re.findall(r'\d*\.?\d+', ingredient.quantity)
                    float_quantity = float(ingredient_quantity[0]) # from ingredient's quantity
                    quantity_unit0 = re.sub(r'\d*\.?\d+', '', ingredient.quantity)
                    quantity_unit = quantity_unit0.replace(' ', '').replace('.','').lower()
                    if(quantity_unit[len(quantity_unit)-1]=='s'):
                        quantity_unit = quantity_unit[:-1]
                    # unit_amount = goal.desired_quantity * float_quantity * sku.formula_scale_factor
                    # unit_amount_str = str(unit_amount) + ' ' + quantity_unit0
                    unit_amount = unit_handling(package_size_unit, quantity_unit, float_quantity, float_package_size, goal.desired_quantity,
                        sku.formula_scale_factor)
                    unit_amount_str = str(round(unit_amount, 3)) + ' ' + package_size_unit0
                    temp.append(unit_amount_str)
                    package_amount = unit_amount/float_package_size
                    package_amount_str = str(round(package_amount, 3)) + ' ' + 'packages'
                    temp.append(package_amount_str)
                    # if not unit_handling(package_size_unit, quantity_unit):
                    #     errors.append('unit not compatible for %s' % ingredient.ig.ingredient_name)
                    #     print(errors)
                    if ingredient.ig.ingredient_name in response:
                        old_list = response[ingredient.ig.ingredient_name]
                        old_list[0] = old_list[0] + temp[0]
                        old_list[1] = old_list[1] + temp[1]
                        response[ingredient.ig.ingredient_name] = old_list
                    else: 
                        response[ingredient.ig.ingredient_name] = temp
                print(response)
                return Response(response,status=status.HTTP_200_OK)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)


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
def skus_to_formula(request,formulaid):
    if(request.method == 'GET'):
        try: 
            skus = Sku.objects.filter(formula=formulaid)
            response = []
            for sku in skus:
                serializer = SkuSerializer(sku)
                response.append(serializer.data)
            return Response(response,status = status.HTTP_200_OK)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/accounts/login/')
@api_view(['GET','POST'])
def formula_to_sku(request,formulaid):
    if(request.method == 'GET'):
        try: 
            formulas = Formula.objects.filter(id=formulaid)
            response=[]
            for formula in formulas:
                serializer = FormulaSerializer(formula)
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
@api_view(['GET','POST'])
def ingredients_to_formula(request,formulaid):
    if(request.method == 'GET'):
        try: 
            ingredients_to_formula = Formula_To_Ingredients.objects.filter(formula=formulaid)
            ids= ingredients_to_formula.values_list("ig",flat=True)
            ingredients = Ingredient.objects.filter(id__in=ids)
            response = []
            for ingredient in ingredients:
                serializer = IngredientSerializer(ingredient)
                for relation in ingredients_to_formula: 
                    if(relation.ig.id == ingredient.id):
                        data = serializer.data
                        data['quantity'] = relation.quantity
                        response.append(data)
            return Response(response,status = status.HTTP_200_OK)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

    def validate_unit(ingredient_quantity_unit, quantity_unit):
        mass = ['lb', 'pound', 'oz', 'ounce', 'ton', 'g', 'gram', 'kg', 'kilogram']
        volume = ['floz', 'fluidounce', 'pt', 'pint', 'qt', 'quart', 'gal', 'gallon', 'ml', 'milliliter', 'l', 'liter']
        count = ['ct', 'count']
        if ingredient_quantity_unit in mass and quantity_unit in mass:
            return True;
        
        if ingredient_quantity_unit in volume and quantity_unit in volume:
            return True

        if ingredient_quantity_unit in count and quantity_unit in count:
            return True

        return False

    if(request.method == 'POST'):
        try: 
            errors = []
            formula = Formula.objects.get(id=formulaid)
            ingredient = Ingredient.objects.get(ingredient_name=request.data['ingredient_name'])
            ingredient_quantity = ingredient.package_size
            quantity = request.data['quantity']
            ingredient_quantity_unit = re.sub(r'\d*\.?\d+', '', ingredient_quantity)
            ingredient_quantity_unit = ingredient_quantity_unit.replace(' ', '').replace('.','').lower()
            if(ingredient_quantity_unit[len(ingredient_quantity_unit)-1]=='s'):
               ingredient_quantity_unit = ingredient_quantity_unit[:-1]
            quantity_unit = re.sub(r'\d*\.?\d+', '', quantity)
            quantity_unit = quantity_unit.replace(' ', '').replace('.','').lower()
            if(quantity_unit[len(quantity_unit)-1]=='s'):
                quantity_unit = quantity_unit[:-1]
            if not validate_unit(ingredient_quantity_unit, quantity_unit):
                errors.append('unit not compatible for %s' % ingredient.ingredient_name)
                post_result = {'errors': errors}
                return Response(post_result, status = status.HTTP_400_BAD_REQUEST)
            newrelation = {'formula':formula.id,'ig':ingredient.id,'quantity':request.data['quantity']}
            serializer = IngredientToFormulaSerializer(data=newrelation)
            if(serializer.is_valid()):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/accounts/login/')
@api_view(['POST'])
def delete_ingredients_to_formula(request,formula,ig):
    try: 
        ingredients_to_formula = Formula_To_Ingredients.objects.get(formula = formula,ig=ig)
        ingredients_to_formula.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)
    except Exception as e: 
        return Response(status = status.HTTP_400_BAD_REQUEST)


@login_required(login_url='/accounts/login/')
@api_view(['POST'])
def update_ingredients_to_formula(request,formula,ig):
    if(request.method == 'POST'):
        try: 
            relation = Formula_To_Ingredients.objects.get(formula = formula, ig=ig)
            serializer = IngredientToFormulaSerializer(relation,{'quantity':request.data['quantity']},partial=True)
            if(serializer.is_valid()):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
            return Response(status = status.HTTP_400_BAD_REQUEST)
        except Exception as e: 
            print(e)
            return Response(status = status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/accounts/login/')
@api_view(['GET'])
def mls_to_sku(request,skuid):
    if(request.method == 'GET'):
        try: 
            mls_to_formula = Sku_To_Ml_Shortname.objects.filter(sku=skuid)
            ml_short_names= mls_to_formula.values_list("ml_short_name",flat=True)
            mls = Manufacture_line.objects.filter(ml_short_name__in=ml_short_names)
            response = []
            for ml in mls:
                serializer = ManufactureLineSerializerSerializer(ml)
                for relation in Sku_To_Ml_Shortname: 
                    if(relation.ml_short_name.ml_short_name == ml.ml_short_name):
                        data = serializer.data
                        # data['quantity'] = relation.quantity
                        response.append(data)
            return Response(response,status = status.HTTP_200_OK)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def add_ml_to_sku(request,skuid,mlshortname):
    # need to check for ml short name uniqueness.
    if(request.method == 'POST'):
        try: 
            sku = Sku.objects.get(id=skuid)
            ml = Ingredient.objects.get(ml_short_name=mlshortname)
            newrelation = {'sku':sku.id,'ml_short_name':ml.ml_short_name}
            serializer = ManufactureLineToSkuSerializer(data=newrelation)
            if(serializer.is_valid()):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e: 
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
    search_term = request.query_params.get('search', None)
    if(request.method == 'GET'):
        try: 
            if search_term:
            # filter skus by sku name
                goals = Manufacture_Goal.objects.filter(
                    Q(user=id),
                    Q(name=goalid),
                    Q(sku__sku_name__icontains=search_term)
                    | Q(sku__productline__product_line_name__icontains=search_term))
            else:
                goals = Manufacture_Goal.objects.filter(user=id,name=goalid)
            # goals = Manufacture_Goal.objects.filter(user=id,name=goalid)
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
            serializer = GoalSerializer(goal,{'goalname':request.data['goalname'],'deadline':request.data['deadline']},partial=True)
            if(serializer.is_valid()):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
            return Response(status = status.HTTP_400_BAD_REQUEST)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def netid_login(request):
    if(request.method == 'POST'):
        try: 
            # Calling Collab Gets
            url = 'https://api.colab.duke.edu/identity/v1/'
            headers = {'x-api-key':'hypo-meals',"Authorization":'Bearer '+request.data['access_token']}
            r = requests.get(url,headers=headers)
            data= r.json()
            username = data['netid']
            password = '(*124aqtn13Qsmt'
            user = User.objects.filter(username=username)
            if(len(user)==0):
                newuser = User.objects.create_user(username,'', password)
                newuser.save()
            # CSRF Token And Logging Into Django
            csrf_client = Client(enforce_csrf_checks=True)
            url = '/accounts/login/?next=/'
            csrf_client.get(url)
            csrftoken = csrf_client.cookies['csrftoken']
            login_data = dict(username=username, password=password, csrfmiddlewaretoken=csrftoken.value, next='/')
            return csrf_client.post(url, data=login_data, headers=dict(Referer=url))
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)


