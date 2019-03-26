from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ViewSetMixin
from .models import *
from .serializers import *
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.middleware.csrf import CsrfViewMiddleware, get_token
from django.test import Client
from django.contrib.auth.models import User
from django.db import transaction
import datetime
import math

import requests
import re

# APIView is specific for handling REST API requests. User need to Explicitly describe  
# the logic for post, get, delete, etc. If not described, action is not allowed. 
# ViewSet simplifies the API logic by providing common actions logic. 
# https://stackoverflow.com/questions/41379654/difference-between-apiview-class-and-viewsets-class/41380941
# https://stackoverflow.com/questions/32589087/django-rest-framework-difference-between-views-and-viewsets
# class SalesReportViewSet(viewsets.ModelViewSet):
#     queryset = Sales.objects.all()
#     serializer_class = SalesSerializer

class SkuViewSet(viewsets.ModelViewSet):
    queryset = Sku.objects.all()
    serializer_class = SkuSerializer

    # GET override
    @transaction.atomic
    def create(self, request, *args, **kwargs): #override post
        try:
            errors = []
            transaction_savepoint = transaction.savepoint()
            post_data = request.data
            sku_id = post_data['id']
            sku_name = post_data['sku_name']
            caseupc = post_data['caseupc']
            unitupc = post_data['unitupc']
            count = post_data['count']
            unit_size = post_data['unit_size']
            productline = post_data['productline']
            formula_id = post_data['formula']
            formula_name = post_data['formula_name']
            formula_scale_factor = post_data['formula_scale_factor']
            manufacture_rate = post_data['manufacture_rate']
            manufacture_setup = post_data['manufacture_setup_cost']
            manufacture_run = post_data['manufacture_run_cost']
            comment = post_data['comment']

            if Formula.objects.filter(id=formula_id).exists():
                formula = Formula.objects.get(id=formula_id)
                f = FormulaSerializer(formula)
                f_data = f.data
                formula.delete()
                f_data['formula_name']=formula_name
                serializer = FormulaSerializer(data=f_data)
                if(serializer.is_valid()):
                    serializer.save()
                else:
                    for error in serializer.errors.values():
                        errors.append(error)
            else:
                serializer = FormulaSerializer(data={
                    'formula_name':formula_name,
                    'id':formula_id,
                    'comment':comment
                })
                if(serializer.is_valid()):
                    serializer.save()
                else:
                    for error in serializer.errors.values():
                        errors.append(error)

            sku_serializer = SkuSerializer(data={'id':sku_id,'productline':productline,'caseupc':caseupc,'unitupc':unitupc,'sku_name':sku_name,'count':count,'unit_size':unit_size,'formula':formula_id,'formula_scale_factor':formula_scale_factor,'manufacture_rate':manufacture_rate,
                'manufacture_setup_cost': manufacture_setup,'manufacture_run_cost':manufacture_run,'comment':comment})
            if(sku_serializer.is_valid()):
                # print(sku_serializer.data)
                sku_serializer.save()
                # return Response(sku_serializer.data,status = status.HTTP_201_CREATED)
            else:
                for error in sku_serializer.errors.values():
                    errors.append(error)
            if errors != []:
                transaction.savepoint_rollback(transaction_savepoint)
                return Response(errors,status = status.HTTP_400_BAD_REQUEST)
            transaction.savepoint_commit(transaction_savepoint)
            return Response(sku_serializer.data,status = status.HTTP_201_CREATED)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

    # @transaction.atomic
    # def update(self, request, *args, **kwargs):
    #     try:
    #         errors = []
    #         transaction_savepoint = transaction.savepoint()
    #         post_data = request.data
    #         sku_id = post_data['id']
    #         sku_name = post_data['sku_name']
    #         caseupc = post_data['caseupc']
    #         unitupc = post_data['unitupc']
    #         count = post_data['count']
    #         unit_size = post_data['unit_size']
    #         productline = post_data['productline']
    #         formula_id = post_data['formula']
    #         if post_data['formula_name']:
    #             formula_name = post_data['formula_name']
    #         formula_scale_factor = post_data['formula_scale_factor']
    #         manufacture_rate = post_data['manufacture_rate']
    #         manufacture_setup = post_data['manufacture_setup_cost']
    #         manufacture_run = post_data['manufacture_run_cost']
    #         comment = post_data['comment']
    #         print(sku_id)

    #         if Formula.objects.filter(id=formula_id).exists():
    #             formula = Formula.objects.get(id=formula_id)
    #             f = FormulaSerializer(formula)
    #             f_data = f.data
    #             formula.delete()
    #             if formula_name:
    #                 f_data['formula_name']=formula_name
    #             serializer = FormulaSerializer(data=f_data)
    #             if(serializer.is_valid()):
    #                 serializer.save()
    #             else:
    #                 for error in serializer.errors.values():
    #                     errors.append(error)
    #         else:
    #             serializer = FormulaSerializer(data={'formula_name':formula_name,'id':formula_id,'comment':comment})
    #             if(serializer.is_valid()):
    #                 serializer.save()
    #             else:
    #                 for error in serializer.errors.values():
    #                     errors.append(error)
    #         print('66')
    #         sku = Sku.objects.get(id=sku_id)
    #         print(sku)
    #         s = SkuSerializer(sku)
    #         s_data = s.data
    #         print(s_data)
    #         print('66')
    #         sku.delete()
    #         print('66')
    #         s_data['sku_name']=sku_name
    #         s_data['productline']=productline
    #         s_data['caseupc']=caseupc
    #         s_data['unitupc']=unitupc
    #         s_data['count']=count
    #         print('66')
    #         s_data['unit_size']=unit_size
    #         s_data['formula']=formula_id
    #         s_data['formula_scale_factor']=formula_scale_factor
    #         print('66')
    #         s_data['manufacture_rate']=manufacture_rate
    #         s_data['comment']=comment
    #         s_data['manufacture_setup_cost'] = manufacture_setup
    #         s_data['manufacture_run_cost'] = manufacture_run
    #         print('66')
    #         sku_serializer = SkuSerializer(data=s_data)
    #         if(sku_serializer.is_valid()):
    #             print(sku_serializer.data)
    #             # sku_serializer.save()
    #             # return Response(sku_serializer.data,status = status.HTTP_201_CREATED)
    #         else:
    #             for error in sku_serializer.errors.values():
    #                 errors.append(error)
    #         if errors != []:
    #             transaction.savepoint_rollback(transaction_savepoint)
    #             return Response(errors,status = status.HTTP_400_BAD_REQUEST)
    #         transaction.savepoint_commit(transaction_savepoint)
    #         return Response(sku_serializer.data,status = status.HTTP_201_CREATED)
    #     except Exception as e: 
    #         return Response(status = status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset,many=True)
        # attach a cell of ml_short_names to skus
        for sku in serializer.data:
            ml_short_names = Sku_To_Ml_Shortname.objects.filter(sku=sku['id']).values_list("ml_short_name",flat=True)
            cell = ','.join(list(ml_short_names))
            sku['ml_short_names'] = '"%s"' % cell
        return Response(serializer.data)

    def get_queryset(self):
        queryset = super().get_queryset()
        search_terms = self.request.query_params.get('search', None)
        if search_terms and ',' in search_terms:
            search_terms = search_terms.split(',')
            first = True
            for search_term in search_terms:
                search_term.strip(',')
                if first:
                    queryset = Sku.objects.filter(Q(sku_name__icontains=search_term) | Q(productline__product_line_name__icontains=search_term)|Q(id__icontains=search_term)|Q(caseupc__icontains=search_term)|Q(unitupc__icontains=search_term))
                    first = False
                else:
                    queryset |= Sku.objects.filter(Q(sku_name__icontains=search_term) | Q(productline__product_line_name__icontains=search_term)|Q(id__icontains=search_term)|Q(caseupc__icontains=search_term)|Q(unitupc__icontains=search_term))
            # obtain all skus whose ingredient names include search_term
                formula_ids = Formula_To_Ingredients.objects.filter(ig__ingredient_name__icontains=search_term).values('formula')
                sku_ids = Sku.objects.filter(formula__id__in=formula_ids).values('id')
                queryset |= Sku.objects.filter(id__in=sku_ids)
        elif search_terms:
            queryset = Sku.objects.filter(Q(sku_name__icontains=search_terms) | Q(productline__product_line_name__icontains=search_terms)|Q(id__icontains=search_terms)|Q(caseupc__icontains=search_terms)|Q(unitupc__icontains=search_terms))
            formula_ids = Formula_To_Ingredients.objects.filter(ig__ingredient_name__icontains=search_terms).values('formula')
            sku_ids = Sku.objects.filter(formula__id__in=formula_ids).values('id')
            queryset |= Sku.objects.filter(id__in=sku_ids)
        return queryset

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    # https://www.django-rest-framework.org/api-guide/filtering/#filtering-against-query-parameters
    def get_queryset(self):
        queryset = super().get_queryset() 
        search_terms = self.request.query_params.get('search', None)
        if search_terms and ',' in search_terms:
            search_terms = search_terms.split(',')
            first = True
            for search_term in search_terms:
                search_term.strip(' ')
                if first: 
                    queryset = Ingredient.objects.filter(Q(ingredient_name__icontains=search_term) | Q(id__icontains=search_term))
                    first = False;
                else:
                    queryset |= Ingredient.objects.filter(Q(ingredient_name__icontains=search_term) | Q(id__icontains=search_term))
                # obtain all ingrs whose name contain search_term
                formula_ids = Sku.objects.filter(sku_name__icontains=search_term).values('formula')
                ingr_ids = Formula_To_Ingredients.objects.filter(formula__in=formula_ids).values('ig')
                queryset |= Ingredient.objects.filter(id__in=ingr_ids)
        elif search_terms:
            queryset = Ingredient.objects.filter(Q(ingredient_name__icontains=search_terms) | Q(id__icontains=search_terms))
            formula_ids = Sku.objects.filter(sku_name__icontains=search_terms).values('formula')
            ingr_ids = Formula_To_Ingredients.objects.filter(formula__in=formula_ids).values('ig')
            queryset |= Ingredient.objects.filter(id__in=ingr_ids)
        return queryset

# class SalesReportViewSet(viewsets.ModelViewSet):
#     queryset = Sale_Record.objects.all()
#     serializer_class = SalesReportSerializer
#     # print('retrive')

#     def retrive(self, request, *args, **kwargs):
#         print('retrive')
#         instance = self.get_object()
#         serializer = self.get_serializer(instance)
#         case_dict = {}
#         revenue_dict = {}
#         for sale_record in serializer.data:
#             year = sale_record['sale_date'].date.today().year;
#             revenue_dict[year] += (sale_record['sales'])*(sale_record['price_per_case'])
#             case_dict[year] += sale_record['sales']
#         print(case_dict)
#         print(revenue_dict)
#         return Response(serializer.data)

class FormulaViewSet(viewsets.ModelViewSet):
    queryset = Formula.objects.all()
    serializer_class = FormulaSerializer

    def destroy(self, request, *args, **kwargs):
        formula = self.get_object()
        # If related skus exist, abandon deletion 
        if Sku.objects.filter(formula=formula.id).exists():
            error = 'Related SKUs exist. Fail to delete Formula #%s' % str(formula.id)
            return Response(error, status = status.HTTP_400_BAD_REQUEST)
        formula.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        queryset = super().get_queryset()
        search_terms = self.request.query_params.get('search', None)
        if search_terms and ',' in search_terms:
            search_terms = search_terms.split(',')
            first = True
            for search_term in search_terms:
                search_term.strip(',')
                if first:
                    queryset = Formula.objects.filter(Q(formula_name__icontains=search_term) | Q(id__icontains=search_term))
                    first = False
                else:
                    queryset |= Formula.objects.filter(Q(formula_name__icontains=search_term) | Q(id__icontains=search_term))
                formula_ids = Formula_To_Ingredients.objects.filter(ig__ingredient_name__icontains=search_term).values('formula')
                queryset |= Formula.objects.filter(id__in=formula_ids)
        elif search_terms:
            # search by formula name, id or ingredient used 
            queryset = Formula.objects.filter(Q(formula_name__icontains=search_terms) | Q(id__icontains=search_terms))
            formula_ids = Formula_To_Ingredients.objects.filter(ig__ingredient_name__icontains=search_terms).values('formula')
            queryset |= Formula.objects.filter(id__in=formula_ids)
        return queryset

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class ManufactureGoalViewSet(viewsets.ModelViewSet):
    queryset = Manufacture_Goal.objects.all()
    serializer_class = ManufactureGoalSerializer
    
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
@api_view(['GET','POST'])
# return a report on manufacture status
def sales_summary(request):
    def costCalculate(quantity, quantity_unit, package_size, package_size_unit, formula_scale_factor, cpp):
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

        if package_size == 0:
            return 0

        num = cpp*formula_scale_factor/package_size

        if package_size_unit in count and quantity_unit in count:
            res = num*(quantity/package_size)
            return res
        elif package_size_unit in mass and quantity_unit in mass:
            mass_converted = (quantity/(mass_dict[quantity_unit]))*mass_dict[package_size_unit]
            # print("converted mass"+str(mass_converted))
            res1 = num*mass_converted
            return res1
        elif package_size_unit in volume and quantity_unit in volume:
            volume_converted = (quantity/(volume_dict[quantity_unit]))*volume_dict[package_size_unit]
            res2 = num*volume_converted
            return res2

        return 0

    if(request.method=='GET'):
        try:
            product_line_names = Product_Line.objects.all()
            product_line_dict = {}
            for pl in product_line_names:
                skus = Sku.objects.filter(productline=pl.product_line_name)
                sku_dict = {}
                response = []
                for sku in skus:
                    year_dict = {}
                    year_dict['overall'] = {}
                    sale_records = Sale_Record.objects.filter(sku=sku.id)
                    ingredients = Formula_To_Ingredients.objects.filter(formula=sku.formula)
                    case_dict = {}
                    setup_cost = sku.manufacture_setup_cost
                    formula_scale_factor = sku.formula_scale_factor
                    overall_rev = 0
                    overall_case = 0
                    avg_run_size = 0
                    avg_setup_cost_per_case = 0
                    ingr_cost_per_case = 0
                    run_cost_per_case = sku.manufacture_run_cost
                    for sale_record in sale_records:
                        sale_date = sale_record.sale_date
                        year = sale_date.year
                        revenue = sale_record.sales * sale_record.price_per_case
                        overall_rev = overall_rev + revenue
                        case = sale_record.sales
                        overall_case = overall_case + case
                        if year in year_dict:
                            old_rev = year_dict[year]['revenue']
                            year_dict[year]['revenue'] = old_rev + revenue
                        else:
                            year_dict[year] = {}
                            year_dict[year]['revenue'] = revenue
                        if year in case_dict:
                            old_case = case_dict[year]
                            case_dict[year] = old_case + case
                        else:
                            case_dict[year] = case
                    # print(year_dict)
                    if case_dict:
                        for key in case_dict:
                            # print(key)
                            avg_rev_per_case = year_dict[key]['revenue']/case_dict[key]
                            year_dict[key]['avg_rev_per_case'] = avg_rev_per_case
                        print(year_dict)
                    for ingr in ingredients:
                        package_size = re.findall(r'\d*\.?\d+', ingr.ig.package_size)
                        package_size_unit0 = re.sub(r'\d*\.?\d+', '', ingr.ig.package_size)
                        package_size_unit = package_size_unit0.replace(' ', '').replace('.','').lower()
                        if(package_size_unit[len(package_size_unit)-1]=='s'):
                            package_size_unit = package_size_unit[:-1]
                        float_package_size = float(package_size[0]) # from ingredient's package size
                        ingredient_quantity = re.findall(r'\d*\.?\d+', ingr.quantity)
                        float_quantity = float(ingredient_quantity[0]) # from ingredient's quantity
                        quantity_unit0 = re.sub(r'\d*\.?\d+', '', ingr.quantity)
                        quantity_unit = quantity_unit0.replace(' ', '').replace('.','').lower()
                        if(quantity_unit[len(quantity_unit)-1]=='s'):
                            quantity_unit = quantity_unit[:-1]
                        cost = costCalculate(float_quantity, quantity_unit, float_package_size, package_size_unit, sku.formula_scale_factor, ingr.ig.cpp)
                        ingr_cost_per_case = ingr_cost_per_case + cost
                    year_dict['overall']['revenue'] = overall_rev
                    if overall_case == 0:
                        year_dict['overall']['avg_rev_per_case'] = 0
                    else:
                        year_dict['overall']['avg_rev_per_case'] = overall_rev/overall_case
                    year_dict['overall']['ingr_cost_per_case'] = ingr_cost_per_case
                    year_dict['overall']['avg_run_size'] = avg_run_size
                    year_dict['overall']['avg_setup_cost_per_case'] = avg_setup_cost_per_case 
                    year_dict['overall']['run_cost_per_case'] = run_cost_per_case
                    cogs_per_case = float(run_cost_per_case) + ingr_cost_per_case + float(avg_setup_cost_per_case)
                    year_dict['overall']['cogs_per_case'] = cogs_per_case
                    profit_per_case = float(year_dict['overall']['avg_rev_per_case']) - cogs_per_case
                    year_dict['overall']['profit_per_case'] = profit_per_case
                    if cogs_per_case == 0:
                        year_dict['overall']['profit_margin'] = -1*100
                    else:
                        profit_margin = (float(year_dict['overall']['avg_rev_per_case'])/cogs_per_case-1)*100
                        temp = round(profit_margin,2)
                        year_dict['overall']['profit_margin'] = temp
                    # print(year_dict)
                    sku_dict[sku.id] = {}
                    sku_dict[sku.id] = year_dict
                # print(sku_dict)
                product_line_dict[pl.product_line_name] = {}
                product_line_dict[pl.product_line_name] = sku_dict
            print(product_line_dict)
            response = product_line_dict
            return Response(response,status = status.HTTP_200_OK)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/accounts/login/')
@api_view(['POST'])
# return a report on manufacture status
def manufacture_schedule_report(request, userid):
    if(request.method=='POST'):
        try: 
            # {'user': user, 'manufacture_line_short_name': ml, 'start_date': start_date, 'end_date': end_date}
            request_info = request.data
            # TODO: parse start and end date
            start_date = request_info['start_date']
            end_date = request_info['end_date']
            # {'skus': [
            # {'sku_name': sku_name, 
            # 'case_quantity': quantity, 
            # 'start': start, 
            # 'end' : end, 
            # 'duration': duration, 
            # 'ingredient_info': ['ingr_name': name, 'ingr_quantity': qty]},
            #  {}
            #  ]
            #  }
            result = {'skus': []}
            # schedule_sku_ids could contain duplicated skus 
            schedule_sku_ids = Manufacture_Line_Skus.objects.filter(Q(user=request_info['user']),
                        Q(manufacture_line_short_name=request_info['manufacture_line_short_name']),
                        Q(start__range=[start_date, end_date]) | Q(end__range=[start_date, end_date])).values_list('id', flat=True)
            for schedule_sku_id in schedule_sku_ids:
                schedule_sku = Manufacture_Line_Skus.objects.get(pk=schedule_sku_id)
                sku = Sku.objects.get(pk=schedule_sku.sku_id)
                sku_name=sku.sku_name
                case_quantity = Manufacture_Goal.objects.get(sku=schedule_sku.id, name=schedule_sku.goal_name).desired_quantity
                start = schedule_sku.start
                end = schedule_sku.end
                duration = schedule_sku.duration
                ingredient_info = []
                sku2ingrs = Formula_To_Ingredients.objects.filter(formula=sku.formula)
                for sku2ingr in sku2ingrs:
                    ingr_name = Ingredient.objects.get(pk=sku2ingr.ig.id).ingredient_name
                    ingredient_info.append({
                        'ingr_name': ingr_name,
                        'ingr_quantity': float(sku2ingr.quantity)*sku.formula_scale_factor
                    })
                sku_info = {
                    'sku_name': sku_name,
                    'case_quantity': case_quantity,
                    'start': start,
                    'end': end,
                    'duration': duration,
                    'ingredient_info': ingredient_info
                }
                result['sku'].append(sku_info)
            return Response(result,status = status.HTTP_200_OK)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

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
            formula2ing = Formula_To_Ingredients.objects.filter(ig=ingredientid)
            response = []
            for f in formula2ing:
                skus = Sku.objects.filter(formula=f.formula)
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
            # ingredients_to_sku = Sku_To_Ingredient.objects.filter(sku=skuid)
            # ids= ingredients_to_sku.values_list("ig",flat=True)
            # ingredients = Ingredient.objects.filter(id__in=ids)
            response = []
            sku_object = Sku.objects.get(id=skuid)
            formula_object = Formula.objects.get(id=sku_object.formula.id)
            formula2ingr = Formula_To_Ingredients.objects.filter(formula=formula_object.id)
            # print(formula2ingr)
            for ingr in formula2ingr:
                ingredients = Ingredient.objects.filter(id=ingr.ig.id)
                # print(ingredients)
                for ing in ingredients:
                    serializer = IngredientSerializer(ing)
                    response.append(serializer.data)
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
@api_view(['GET','POST'])
def sku_drilldown(request,skuid):
    if(request.method == 'GET'):
        try: 
           
            return Response(response,status = status.HTTP_200_OK)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)
    if(request.method == 'POST'):
        try: 
            
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
            formula = Formula.objects.get(id=formula)
            ingredient = Ingredient.objects.get(id=ig)
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
            relation = Formula_To_Ingredients.objects.get(formula = formula, ig=ig)
            quantity = request.data['quantity']
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
def mg_to_skus(request,goal_name):
    if(request.method == 'GET'):
        try: 
            response = {}
            response[goal_name]={}
            # get skus associated with the goal: Manufacture_Goal
            sku_ids = Manufacture_Goal.objects.filter(name__goalname=goal_name).values_list('sku', flat=True)
            skus = Sku.objects.filter(id__in=sku_ids)
            goal = Goal.objects.get(goalname=goal_name)
            response[goal_name]['deadline'] = goal.deadline
            for sku in skus:
                # get mls for each sku: Sku_To_Ml_Shortname
                ml_short_names = Sku_To_Ml_Shortname.objects.filter(sku=sku.id).values_list("ml_short_name",flat=True)
                # get time needed for each sku: Sku, Manufacture_Goal
                manufacture_rate = sku.manufacture_rate
                desired_quantity = Manufacture_Goal.objects.get(sku=sku.id, name__goalname=goal_name).desired_quantity
                hours_needed = desired_quantity / manufacture_rate
                response[goal_name][sku.sku_name] = {
                    'manufacturing_lines': list(ml_short_names),
                    'hours_needed': math.ceil(hours_needed),
                }
            return Response(response,status = status.HTTP_200_OK)
        except Exception as e: 
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
            # print(request.data['name'])
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
@api_view(['GET'])
def search_goals(request,search):
    if(request.method == 'GET'):
        try:
            allgoals = Goal.objects.filter(goalname__icontains=search)
            response = []
            for goal in allgoals: 
                response.append(goal.goalname)
            return Response(response,status = status.HTTP_200_OK)
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

@login_required(login_url='/accounts/login/')
@api_view(['POST'])
def save_scheduler(request):
    if(request.method == 'POST'):
        try:
            timeline_data = Scheduler.objects.all()
            if(len(timeline_data)==0):
                serializer = SchedulerSerializer(data=request.data)
                if(serializer.is_valid()):
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
            else: 
                first = timeline_data.first()
                serializer = SchedulerSerializer(first,request.data)
                if(serializer.is_valid()):
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/accounts/login/')
@api_view(['GET'])
def get_scheduler(request):
    if(request.method=='GET'):
        try:
            timeline_data = Scheduler.objects.all()
            if(len(timeline_data)!=0):
                first = timeline_data.first()
                response = {}
                response['items'] = first.items
                response['groups'] = first.groups
                response['scheduled_goals'] = first.scheduled_goals
                response['unscheduled_goals'] = first.unscheduled_goals
                response['manufacturing_lines'] = first.manufacturing_lines
                return Response(response,status = status.HTTP_200_OK)
            else:
                response = {}
                response = {'init':'yes'}
                return Response(response,status = status.HTTP_200_OK)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

