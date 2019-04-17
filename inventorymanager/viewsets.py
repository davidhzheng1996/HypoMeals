from rest_framework import viewsets, filters
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ViewSetMixin
from .models import *
from .serializers import *
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.middleware.csrf import CsrfViewMiddleware, get_token
from django.test import Client
from django.db import transaction
import datetime
import math
from datetime import timedelta
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import Crawler
from scrapy import signals
from scrapy.utils.project import get_project_settings
from scrapy.settings import Settings
import os
import imp
import statistics
from django.db.models import Sum, F, Count
import sys
from scrapyd_api import ScrapydAPI
from rest_framework.permissions import BasePermission


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

# Permissions

# Custom permission for users with "is_active" = True.
class IsAnalyst(BasePermission):
    """
    Allows access only to "is_active" users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_analyst

# =================END PERMISSIONS===============

class SkuViewSet(viewsets.ModelViewSet):
    queryset = Sku.objects.all()
    serializer_class = SkuSerializer
    # permission_classes = ((IsAnalyst, ))

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
                serializer = FormulaSerializer(formula,{'formula_name':formula_name},partial=True)
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

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            super().update(request, *args, **kwargs) 
            update_activity()
            return Response(status = status.HTTP_201_CREATED)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

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
        # queryset = super().get_queryset(request)
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

    if(request.method=='POST'):
        try:
            active_pls = request.data['pl']
            customer = request.data['customer']
            product_line_names = []
            if active_pls:
                for a in active_pls:
                    product_line_names.append(Product_Line.objects.get(product_line_name=a))
            else:
                product_line_names = Product_Line.objects.all()
            product_line_dict = {}
            for pl in product_line_names:
                total_dict = {}
                skus = Sku.objects.filter(productline=pl.product_line_name)
                pl_rev = Sale_Record.objects.filter(sku__productline=pl.product_line_name).aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                first_pl_rev = Sale_Record.objects.filter(sku__productline=pl.product_line_name,sale_date__year='2010').aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                second_pl_rev = Sale_Record.objects.filter(sku__productline=pl.product_line_name,sale_date__year='2011').aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                third_pl_rev = Sale_Record.objects.filter(sku__productline=pl.product_line_name,sale_date__year='2012').aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                fourth_pl_rev = Sale_Record.objects.filter(sku__productline=pl.product_line_name,sale_date__year='2013').aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                fifth_pl_rev = Sale_Record.objects.filter(sku__productline=pl.product_line_name,sale_date__year='2014').aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                sixth_pl_rev = Sale_Record.objects.filter(sku__productline=pl.product_line_name,sale_date__year='2015').aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                seventh_pl_rev = Sale_Record.objects.filter(sku__productline=pl.product_line_name,sale_date__year='2016').aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                eighth_pl_rev = Sale_Record.objects.filter(sku__productline=pl.product_line_name,sale_date__year='2017').aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                ninenth_pl_rev = Sale_Record.objects.filter(sku__productline=pl.product_line_name,sale_date__year='2018').aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                tenth_pl_rev = Sale_Record.objects.filter(sku__productline=pl.product_line_name,sale_date__year='2019').aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                if first_pl_rev:
                    total_dict[2010] = first_pl_rev
                if second_pl_rev:
                    total_dict[2011] = second_pl_rev
                if third_pl_rev:
                    total_dict[2012] = third_pl_rev
                if fourth_pl_rev:
                    total_dict[2013] = fourth_pl_rev
                if fifth_pl_rev:
                    total_dict[2014] = fifth_pl_rev
                if sixth_pl_rev:
                    total_dict[2015] = sixth_pl_rev
                if seventh_pl_rev:
                    total_dict[2016] = seventh_pl_rev
                if eighth_pl_rev:
                    total_dict[2017] = eighth_pl_rev
                if ninenth_pl_rev:
                    total_dict[2018] = ninenth_pl_rev
                if tenth_pl_rev:
                    total_dict[2019] = tenth_pl_rev
                if pl_rev:
                    total_dict['overall'] = pl_rev
                sku_dict = {}
                response = []
                for sku in skus:
                    year_dict = {}
                    year_dict['overall'] = {}
                    ingredients = Formula_To_Ingredients.objects.filter(formula=sku.formula)
                    formula_scale_factor = sku.formula_scale_factor
                    setup_cost = sku.manufacture_setup_cost
                    ingr_cost_per_case = 0
                    run_cost_per_case = sku.manufacture_run_cost
                    overall_case = Sale_Record.objects.filter(sku=sku.id).aggregate(Sum('sales')).get('sales__sum',0.00)
                    overall_rev = Sale_Record.objects.filter(sku=sku.id).aggregate(total_spent=Sum(F('sales') * F('price_per_case'),   
                    output_field=models.FloatField()
                    )).get('total_spent', 0.00)
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
                    count = Manufacture_Goal.objects.filter(sku=sku.id).count()
                    size = Manufacture_Goal.objects.filter(sku=sku.id).aggregate(Sum('desired_quantity')).get('desired_quantity__sum',0.00)
                    if not count:
                        avg_run_size = 10
                    else:
                        avg_run_size = size/count
                    if not size:
                        avg_setup_cost_per_case = float(setup_cost)/10.0
                    else:
                        avg_setup_cost_per_case = float(setup_cost)/avg_run_size
                    # print(overall_case)
                    if not overall_case:
                        year_dict['overall']['avg_rev_per_case'] = 0
                    else:
                        year_dict['overall']['avg_rev_per_case'] = round(overall_rev/overall_case,2)
                    year_dict['overall']['ingr_cost_per_case'] = round(ingr_cost_per_case,2)
                    year_dict['overall']['avg_run_size'] = avg_run_size
                    year_dict['overall']['avg_setup_cost_per_case'] = round(avg_setup_cost_per_case,2) 
                    year_dict['overall']['run_cost_per_case'] = run_cost_per_case
                    cogs_per_case = float(run_cost_per_case) + ingr_cost_per_case + float(avg_setup_cost_per_case)
                    year_dict['overall']['cogs_per_case'] = round(cogs_per_case,2)
                    profit_per_case = float(year_dict['overall']['avg_rev_per_case']) - cogs_per_case
                    year_dict['overall']['profit_per_case'] = round(profit_per_case,2)
                    if cogs_per_case == 0:
                        year_dict['overall']['profit_margin'] = -1*100
                    else:
                        profit_margin = (float(year_dict['overall']['avg_rev_per_case'])/cogs_per_case-1)*100
                        temp = round(profit_margin,2)
                        year_dict['overall']['profit_margin'] = str(temp)+"%"
                    first_case = Sale_Record.objects.filter(sku=sku.id,sale_date__year='2010').aggregate(Sum('sales')).get('sales__sum',0.00)
                    first_rev = Sale_Record.objects.filter(sku=sku.id,sale_date__year='2010').aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                    second_case = Sale_Record.objects.filter(sku=sku.id,sale_date__year='2011').aggregate(Sum('sales')).get('sales__sum',0.00)
                    second_rev = Sale_Record.objects.filter(sku=sku.id,sale_date__year='2011').aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                    third_case = Sale_Record.objects.filter(sku=sku.id,sale_date__year='2012').aggregate(Sum('sales')).get('sales__sum',0.00)
                    third_rev = Sale_Record.objects.filter(sku=sku.id,sale_date__year='2012').aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                    fourth_case = Sale_Record.objects.filter(sku=sku.id,sale_date__year='2013').aggregate(Sum('sales')).get('sales__sum',0.00)
                    fourth_rev = Sale_Record.objects.filter(sku=sku.id,sale_date__year='2013').aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                    fifth_case = Sale_Record.objects.filter(sku=sku.id,sale_date__year='2014').aggregate(Sum('sales')).get('sales__sum',0.00)
                    fifth_rev = Sale_Record.objects.filter(sku=sku.id,sale_date__year='2014').aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                    sixth_case = Sale_Record.objects.filter(sku=sku.id,sale_date__year='2015').aggregate(Sum('sales')).get('sales__sum',0.00)
                    sixth_rev = Sale_Record.objects.filter(sku=sku.id,sale_date__year='2015').aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                    seventh_case = Sale_Record.objects.filter(sku=sku.id,sale_date__year='2016').aggregate(Sum('sales')).get('sales__sum',0.00)
                    seventh_rev = Sale_Record.objects.filter(sku=sku.id,sale_date__year='2016').aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                    eighth_case = Sale_Record.objects.filter(sku=sku.id,sale_date__year='2017').aggregate(Sum('sales')).get('sales__sum',0.00)
                    eighth_rev = Sale_Record.objects.filter(sku=sku.id,sale_date__year='2017').aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                    nineth_case = Sale_Record.objects.filter(sku=sku.id,sale_date__year='2018').aggregate(Sum('sales')).get('sales__sum',0.00)
                    nineth_rev = Sale_Record.objects.filter(sku=sku.id,sale_date__year='2018').aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                    tenth_case = Sale_Record.objects.filter(sku=sku.id,sale_date__year='2019').aggregate(Sum('sales')).get('sales__sum',0.00)
                    tenth_rev = Sale_Record.objects.filter(sku=sku.id,sale_date__year='2019').aggregate(total_spent=Sum(F('sales') * F('price_per_case'),
                    output_field=models.FloatField())).get('total_spent',0.00)
                    if first_rev:
                        year_dict[2010] = {}
                        year_dict[2010]['revenue'] = first_rev
                    if second_rev:
                        year_dict[2011] = {}
                        year_dict[2011]['revenue'] = second_rev
                    if third_rev: 
                        year_dict[2012] = {}   
                        year_dict[2012]['revenue'] = third_rev
                    if fourth_rev:
                        year_dict[2013] = {}
                        year_dict[2013]['revenue'] = fourth_rev
                    if fifth_rev:
                        year_dict[2014] = {}
                        year_dict[2014]['revenue'] = fifth_rev
                    if sixth_rev:
                        year_dict[2015] = {}
                        year_dict[2015]['revenue'] = sixth_rev
                    if seventh_rev:
                        year_dict[2016] = {}
                        year_dict[2016]['revenue'] = seventh_rev
                    if eighth_rev:
                        year_dict[2017] = {}
                        year_dict[2017]['revenue'] = eighth_rev
                    if nineth_rev:
                        year_dict[2018] = {}
                        year_dict[2018]['revenue'] = nineth_rev
                    if tenth_rev:
                        year_dict[2019] = {}
                        year_dict[2019]['revenue'] = tenth_rev
                    if first_case:
                        year_dict[2010]['avg_rev_per_case'] = round(first_rev/first_case, 2)
                    if second_case:
                        year_dict[2011]['avg_rev_per_case'] = round(second_rev/second_case, 2)
                    if third_case:
                        year_dict[2012]['avg_rev_per_case'] = round(third_rev/third_case, 2)
                    if fourth_case:
                        year_dict[2013]['avg_rev_per_case'] = round(fourth_rev/fourth_case, 2)
                    if fifth_case:
                        year_dict[2014]['avg_rev_per_case'] = round(fifth_rev/fifth_case, 2)
                    if sixth_case:
                        year_dict[2015]['avg_rev_per_case'] = round(sixth_rev/sixth_case, 2)
                    if seventh_case:
                        year_dict[2016]['avg_rev_per_case'] = round(seventh_rev/seventh_case, 2)
                    if eighth_case:
                        year_dict[2017]['avg_rev_per_case'] = round(eighth_rev/eighth_case, 2)
                    if nineth_case:
                        year_dict[2018]['avg_rev_per_case'] = round(nineth_rev/nineth_case, 2)
                    if tenth_case:
                        year_dict[2019]['avg_rev_per_case'] = round(tenth_rev/tenth_case, 2)
                    # print(year_dict)
                    # key = sku.sku_name + ' ' + '#' + str(sku.id)
                    sku_dict[sku.id] = {}
                    sku_dict[sku.id] = year_dict
                # print(sku_dict)
                product_line_dict[pl.product_line_name] = {}
                product_line_dict[pl.product_line_name]['total'] = {}
                product_line_dict[pl.product_line_name]['total'] = total_dict
                product_line_dict[pl.product_line_name]['sku'] = {}
                product_line_dict[pl.product_line_name]['sku'] = sku_dict
                # product_line_dict[pl.product_line_name] = sku_dict
            response = product_line_dict
            return Response(response,status = status.HTTP_200_OK)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/accounts/login/')
@api_view(['POST'])
# return a report on manufacture status
def get_sku_drilldown(request, skuid):
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

    if(request.method=='POST'):
        try:
            result = []
            timespan = request.data['timespan']
            customer = request.data['customer']
            sale_records = Sale_Record.objects.filter(sku=skuid)
            sku = Sku.objects.get(id=skuid)
            ingredients = Formula_To_Ingredients.objects.filter(formula=sku.formula)
            # goals = Manufacture_Goal.objects.filter(sku=skuid)
            response = {}
            count = 0
            # total_rev = 0
            # cases = 0
            setup_cost = sku.manufacture_setup_cost
            ingr_cost_per_case = 0
            run_cost_per_case = sku.manufacture_run_cost
            overall_case = Sale_Record.objects.filter(sku=sku.id).aggregate(Sum('sales')).get('sales__sum',0.00)
            overall_rev = Sale_Record.objects.filter(sku=sku.id).aggregate(total_spent=Sum(F('sales') * F('price_per_case'),   
            output_field=models.FloatField()
            )).get('total_spent', 0.00)
            for sale_record in sale_records:
                # print(sale_record.sku.productline.product_line_name)
                sale_date = sale_record.sale_date
                customer_id = sale_record.customer_id.id
                if customer and customer != 'all':
                    if customer!=str(customer_id):
                        continue
                if timespan['start_date'] and timespan['end_date']:
                    start_date = datetime.datetime.strptime(timespan['start_date'], '%Y-%m-%d').date()
                    end_date = datetime.datetime.strptime(timespan['end_date'], '%Y-%m-%d').date()
                    if sale_date < start_date or sale_date > end_date:
                        continue
                revenue = sale_record.sales * sale_record.price_per_case
                # cases = cases + sale_record.sales
                # total_rev = total_rev + revenue
                year = sale_date.year
                week = sale_date.isocalendar()[1]
                sale_info = {
                    'sale_date': sale_date,
                    'year': year,
                    'week': week,
                    'customer_id': sale_record.customer_id.id,
                    'customer_name': sale_record.customer_name,
                    'sales': sale_record.sales,
                    'price_per_case': sale_record.price_per_case,
                    'revenue': revenue
                }
                result.append(sale_info)
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
            count = Manufacture_Goal.objects.filter(sku=sku.id).count()
            size = Manufacture_Goal.objects.filter(sku=sku.id).aggregate(Sum('desired_quantity')).get('desired_quantity__sum',0.00)
            # for goal in goals:
            #     size = size + goal.desired_quantity
            #     count = count + 1;
            if not count:
                avg_run_size = 10
            else:
                avg_run_size = size/count
            if not size:
                avg_setup_cost_per_case = float(setup_cost)/10.0
            else:
                avg_setup_cost_per_case = float(setup_cost)/avg_run_size
            if not overall_case:
                avg_rev_per_case = 0
            else:
                avg_rev_per_case = round(overall_rev/overall_case,2)
            cogs_per_case = round(float(run_cost_per_case) + float(ingr_cost_per_case) + float(avg_setup_cost_per_case),2)
            profit_per_case = round(float(avg_rev_per_case) - cogs_per_case,2)
            if cogs_per_case == 0:
                year_dict['overall']['profit_margin'] = -1*100
            else:
                profit_margin = (float(avg_rev_per_case)/cogs_per_case-1)*100
                temp = round(profit_margin,2)
            response['overall'] = {
                'revenue': overall_rev,
                'avg_rev_per_case': avg_rev_per_case,
                'ingr_cost_per_case': round(ingr_cost_per_case,2),
                'avg_run_size': avg_run_size,
                'avg_setup_cost_per_case': round(avg_setup_cost_per_case,2),
                'run_cost_per_case': run_cost_per_case,
                'cogs_per_case': cogs_per_case,
                'profit_per_case': profit_per_case,
                'profit_margin': str(temp)+'%'
            }
            response['rows'] = result #map to a list, each entry of the list is a map
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
@api_view(['GET'])
# return list of all manufacturing lines with status 
def get_customer(request):
    if(request.method=='GET'):
        try:
            response = []
            customers = Customer.objects.all()
            for customer in customers:
                serializer = CustomerSerializer(customer)
                response.append(serializer.data)
            return Response(response,status = status.HTTP_200_OK)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/accounts/login/')
@api_view(['POST'])
# return sales projections based on month and day
def get_sales_projection(request):
    def validateDate(date_dict):
        month = int(date_dict['month'])
        day = int(date_dict['day'])
        days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if not date_dict['month'] or not date_dict['day']:
            return False
        if month < 1 or month > 12:
            return False
        if day < 1 or day > days[month]:
            return False
        return True
    # def checkDate(start_dict, end_dict):
    #     month1 = int(start_dict['month'])
    #     month2 = int(end_dict['month'])
    #     day1 = int(start_dict['day'])
    #     day2 = int(end_dict['day'])
    #     if month1 > month2:
    #         return False
    #     elif month1 == month2:
    #         if day1 > day2:
    #             return False
    #     return True
    if(request.method=='POST'):
        try:
            response = {}
            sales = []
            output_dict = {}
            output_dict['rows'] = {}
            sku = Sku.objects.get(sku_name=request.data['sku_name'])
            if not validateDate(request.data['start_date']):
                post_result = 'error: start_date is invalid'
                return Response(post_result, status = status.HTTP_400_BAD_REQUEST)
            if not validateDate(request.data['end_date']):
                post_result = 'error: end_date is invalid'
                return Response(post_result, status = status.HTTP_400_BAD_REQUEST)
            month1 = int(request.data['start_date']['month'])
            month2 = int(request.data['end_date']['month'])
            day1 = int(request.data['start_date']['day'])
            day2 = int(request.data['end_date']['day'])
            d = datetime.datetime.today().strftime('%Y-%m-%d')
            curr_year = datetime.datetime.today().year
            start_month = request.data['start_date']['month']
            start_day = request.data['start_date']['day']
            end_month = request.data['end_date']['month']
            end_day = request.data['end_date']['day']
            prev_year = curr_year
            if month1 > month2:
                prev_year = curr_year - 1
            elif month1 == month2 and day1 > day2:
                prev_year = curr_year - 1
            elif month1 == month2 and day1 == day2:
                post_result = 'error: end_date and start_date are the same'
                return Response(post_result, status = status.HTTP_400_BAD_REQUEST)
            if int(start_month) < 10:
                start_month = '0'+start_month
            if int(start_day) < 10:
                start_day = '0' + start_day
            if int(end_month) < 10:
                end_month = '0'+end_month
            if int(end_day) < 10:
                end_day = '0' + end_day
            start_str = str(prev_year)+start_month+start_day
            end_str = str(curr_year)+end_month+end_day
            start_datetime = datetime.datetime.strptime(start_str, '%Y%m%d')
            start_date = start_datetime.strftime('%Y-%m-%d')
            end_datetime = datetime.datetime.strptime(end_str, '%Y%m%d')
            end_date = end_datetime.strftime('%Y-%m-%d')

            # 2018
            s2018 = str(prev_year-1)+start_month+start_day
            start_datetime_2018 = datetime.datetime.strptime(s2018, '%Y%m%d')
            start_date_2018 = start_datetime_2018.strftime('%Y-%m-%d')
            end2018 = str(curr_year-1)+end_month+end_day
            end_datetime_2018 = datetime.datetime.strptime(end2018, '%Y%m%d')
            end_date_2018 = end_datetime_2018.strftime('%Y-%m-%d')
            sales2018 = Sale_Record.objects.filter(sku=sku.id,sale_date__range=[start_date_2018,end_date_2018]).aggregate(Sum('sales')).get('sales__sum',0.00)
            sales.append(sales2018)
            # 2017
            s2017 = str(prev_year-2)+start_month+start_day
            start_datetime_2017 = datetime.datetime.strptime(s2017, '%Y%m%d')
            start_date_2017 = start_datetime_2017.strftime('%Y-%m-%d')
            end2017 = str(curr_year-2)+end_month+end_day
            end_datetime_2017 = datetime.datetime.strptime(end2017, '%Y%m%d')
            end_date_2017 = end_datetime_2017.strftime('%Y-%m-%d')
            sales2017 = Sale_Record.objects.filter(sku=sku.id,sale_date__range=[start_date_2017,end_date_2017]).aggregate(Sum('sales')).get('sales__sum',0.00)
            sales.append(sales2017)
            # 2016
            s2016 = str(prev_year-3)+start_month+start_day
            start_datetime_2016 = datetime.datetime.strptime(s2016, '%Y%m%d')
            start_date_2016 = start_datetime_2016.strftime('%Y-%m-%d')
            end2016 = str(curr_year-3)+end_month+end_day
            end_datetime_2016 = datetime.datetime.strptime(end2016, '%Y%m%d')
            end_date_2016 = end_datetime_2016.strftime('%Y-%m-%d')
            sales2016 = Sale_Record.objects.filter(sku=sku.id,sale_date__range=[start_date_2016,end_date_2016]).aggregate(Sum('sales')).get('sales__sum',0.00)
            sales.append(sales2016)

            if end_date < d:
                sales2019 = Sale_Record.objects.filter(sku=sku.id,sale_date__range=[start_date,end_date]).aggregate(Sum('sales')).get('sales__sum',0.00)
                sales.append(sales2019)
                output_dict['rows'][curr_year-3] = {
                    'start_date': start_date_2016,
                    'end_date': end_date_2016,
                    'sales': sales2016
                }
                output_dict['rows'][curr_year-2] = {
                    'start_date': start_date_2017,
                    'end_date': end_date_2017,
                    'sales': sales2017
                }
                output_dict['rows'][curr_year-1] = {
                    'start_date': start_date_2018,
                    'end_date': end_date_2018,
                    'sales': sales2018
                }
                output_dict['rows'][curr_year] = {
                    'start_date': start_date,
                    'end_date': end_date,
                    'sales': sales2019
                }
            else:
                s2015 = str(prev_year-4)+start_month+start_day
                start_datetime_2015 = datetime.datetime.strptime(s2015, '%Y%m%d')
                start_date_2015 = start_datetime_2015.strftime('%Y-%m-%d')
                end2015 = str(curr_year-4)+end_month+end_day
                end_datetime_2015 = datetime.datetime.strptime(end2015, '%Y%m%d')
                end_date_2015 = end_datetime_2015.strftime('%Y-%m-%d')
                sales2015 = Sale_Record.objects.filter(sku=sku.id,sale_date__range=[start_date_2015,end_date_2015]).aggregate(Sum('sales')).get('sales__sum',0.00)
                sales.append(sales2015)
                output_dict['rows'][curr_year-4] = {
                    'start_date': start_date_2015,
                    'end_date': end_date_2015,
                    'sales': sales2015
                }
                output_dict['rows'][curr_year-3] = {
                    'start_date': start_date_2016,
                    'end_date': end_date_2016,
                    'sales': sales2016
                }
                output_dict['rows'][curr_year-2] = {
                    'start_date': start_date_2017,
                    'end_date': end_date_2017,
                    'sales': sales2017
                }
                output_dict['rows'][curr_year-1] = {
                    'start_date': start_date_2018,
                    'end_date': end_date_2018,
                    'sales': sales2018
                }
            sales_avg = round(sum(sales)/len(sales))
            sales_std = statistics.stdev(sales)
            sales_std = round(sales_std,1)
            temp_str = '<'+str(sales_avg)+'>'+'+/-'+'<'+str(sales_std)+'>'
            # output_dict['overall'] = [sales_avg,sales_std]
            output_dict['summary'] = temp_str
            output_dict['sales_avg'] = sales_avg
            response = output_dict
            # print(response)
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
        mass_dict['ton'] = 0.000984
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
                # print(sku.sku_name)
                formula = sku.formula
                ingredients = Formula_To_Ingredients.objects.filter(formula = formula)
                for ingredient in ingredients: 
                    print(ingredient.ig.ingredient_name)
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
                        old_amount = re.findall(r'\d*\.?\d+', old_list[0])
                        float_old_amount = float(old_amount[0])
                        new_amount = unit_amount + float_old_amount
                        new_amount_str = str(round(new_amount, 3)) + ' ' + package_size_unit0
                        old_package = re.findall(r'\d*\.?\d+', old_list[1])
                        float_old_package = float(old_package[0])
                        new_package = package_amount + float_old_package
                        new_package_str = str(round(new_package, 3)) + ' ' + 'packages'
                        old_list[0] = new_amount_str
                        old_list[1] = new_package_str
                        response[ingredient.ig.ingredient_name] = old_list
                    else: 
                        response[ingredient.ig.ingredient_name] = temp
            # print(response)
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
            if not sku_ids:
                post_result = goal_name +' does not exist'
                return Response(post_result, status = status.HTTP_400_BAD_REQUEST)
            skus = Sku.objects.filter(id__in=sku_ids)
            goal = Goal.objects.get(goalname=goal_name)
            if goal.enable_goal == False:
                post_result = goal_name +' is not enabled'
                return Response(post_result, status = status.HTTP_400_BAD_REQUEST)
            # print(goal)
            response[goal_name]['deadline'] = goal.deadline
            for sku in skus:
                # get mls for each sku: Sku_To_Ml_Shortname
                ml_short_names = Sku_To_Ml_Shortname.objects.filter(sku=sku.id).values_list("ml_short_name",flat=True)
                # get time needed for each sku: Sku, Manufacture_Goal
                manufacture_rate = sku.manufacture_rate
                desired_quantity = Manufacture_Goal.objects.get(sku=sku.id, name__goalname=goal_name).desired_quantity
                if manufacture_rate == 0:
                    hours_needed = 0
                else:
                    hours_needed = desired_quantity / manufacture_rate
                
                if not Manufacturing_Activity.objects.filter(sku=sku.id, goal_name=goal_name).exists():
                    response[goal_name][sku.sku_name] = {
                        'manufacturing_lines': list(ml_short_names),
                        'hours_needed': math.ceil(hours_needed)
                    }
                    # add sku as a new manufacture activity 
                    # user, manufacturing line, start, end, duration are registered using random values
                    serializer = ManufacturingActivitySerializer(data={
                        'user': 1,
                        'manufacturing_line': ml_short_names[0],
                        'sku': sku.id,
                        'goal_name': goal_name,
                        'start': datetime.datetime.now(),
                        'end': datetime.datetime.now(),
                        'duration': math.ceil(hours_needed),
                        'status': 'inactive'
                    })
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)  
            if len(response[goal_name]) == 1:
                response = {} 
            return Response(response,status = status.HTTP_200_OK)
        except Exception as error: 
            print(error)
            return Response(status = status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/accounts/login/')
@api_view(['GET'])
def remove_mg(request,goal_name):
    if(request.method == 'GET'):
        try: 
            Manufacturing_Activity.objects.filter(goal_name=goal_name).delete()
            return Response(status = status.HTTP_200_OK)
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
            # goal = Goal.objects.get(id=request.data['name'])
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
def manufacture_goals_get(request,goalid):
    search_term = request.query_params.get('search', None)
    if(request.method == 'GET'):
        try: 
            if search_term:
            # filter skus by sku name
                goals = Manufacture_Goal.objects.filter(
                    Q(name=goalid),
                    Q(sku__sku_name__icontains=search_term)
                    | Q(sku__productline__product_line_name__icontains=search_term))
            else:
                goals = Manufacture_Goal.objects.filter(name=goalid)
            # goals = Manufacture_Goal.objects.filter(user=id,name=goalid)
            response = []
            for goal in goals:
                serializer = ManufactureGoalSerializer(goal)
                response.append(serializer.data)
            print(response)
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
            serializer = ManufactureGoalSerializer(manufacture_goal,{'desired_quantity':request.data['desired_quantity'],'comment':request.data['comment'],'timestamp':request.data['timestamp']},partial=True)
            if(serializer.is_valid()):
                serializer.save()
                update_activity()
                return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
            return Response(status = status.HTTP_400_BAD_REQUEST)
        except Exception as e: 
            print(e)
            return Response(status = status.HTTP_400_BAD_REQUEST)

# Singular Manufacturing Goal
@login_required(login_url='/accounts/login/')
@api_view(['GET','POST'])
def goal(request):
    if(request.method == 'GET'):
        try: 
            goals = Goal.objects.all()
            print('hi')
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
                if goal.enable_goal == False:
                    continue
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
def update_goal(request,goalid):
    if(request.method == 'POST'):
        try: 
            goal = Goal.objects.get(id=goalid)
            serializer = GoalSerializer(goal,{'goalname':request.data['goalname'],'deadline':request.data['deadline'],'enable_goal':request.data['enable_goal'],'timestamp':request.data['timestamp']},partial=True)
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
            print('SAVE request')
            print(request.data)
            if len(request.data) == 0:
                return Response(request.data, status=status.HTTP_204_NO_CONTENT)
            for activity in request.data:
                sku_id = Sku.objects.filter(sku_name=activity['sku']).values_list("id",flat=True)[0]
                activity['sku'] = sku_id
                # if activity already exists, update
                if Manufacturing_Activity.objects.filter(user=activity['user'], sku=activity['sku'], goal_name=activity['goal_name']).exists():
                    exist_activity = Manufacturing_Activity.objects.get(user=activity['user'], sku=activity['sku'], goal_name=activity['goal_name'])
                    serializer = ManufacturingActivitySerializer(exist_activity, data={
                        'manufacturing_line': activity['manufacturing_line'],
                        'start': activity['start'],
                        'end': activity['end'],
                        'duration': activity['duration'],
                        'status': activity['status']
                    }, partial=True)
                else:
                    serializer = ManufacturingActivitySerializer(data=activity)
                if serializer.is_valid():
                    serializer.save()
                else:
                    print(serializer.errors)
                    return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST) 
            return Response(request.data, status=status.HTTP_204_NO_CONTENT)
        except Exception as e: 
            print(e)
            return Response(e, status = status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/accounts/login/')
@api_view(['GET'])
def get_scheduler(request):
    if(request.method=='GET'):
        try:
            # get scheduler data from manufacture activity model 
            activities = Manufacturing_Activity.objects.all()
            if len(activities) == 0:
                response = {}
                response = {'init':'yes'}
                return Response(response,status = status.HTTP_200_OK)
            for manufacture_activity in activities:
                goal = Goal.objects.get(goalname = manufacture_activity.goal_name.goalname)
                if goal.enable_goal == False and manufacture_activity.status == 'active':
                    serializer = ManufacturingActivitySerializer(manufacture_activity,{'status':'orphaned'},partial=True)
                    if(serializer.is_valid()):
                        serializer.save()
                elif goal.enable_goal == True and manufacture_activity.status == 'orphaned':
                    serializer = ManufacturingActivitySerializer(manufacture_activity,{'status':'active'},partial=True)
                    if(serializer.is_valid()):
                        serializer.save()
                elif goal.enable_goal == False and manufacture_activity.status == 'inactive':
                    manufacture_activity.delete()
            response = {
                # all activities, including inactive ones
                'activities': [],
                # [{goal_name(enabled): {sku_name(active),}},]
                # for keeping track of goals and activities already-scheduled
                'scheduled_goals': [],
                # [{goal_name(enabled): {sku_name(non_active),},]
                # for visualizing goals and activities to-be-scheduled
                'unscheduled_goals': [],
            }
            # add items
            for m_activity in activities:
                activity = ManufacturingActivitySerializer(m_activity).data
                sku_name = Sku.objects.get(id=activity['sku']).sku_name
                allowed_manufacturing_lines = Sku_To_Ml_Shortname.objects.filter(sku=activity['sku']).values_list('ml_short_name', flat=True)
                allowed_manufacturing_lines = list(allowed_manufacturing_lines)
                deadline = Goal.objects.get(goalname=activity['goal_name']).deadline
                # print(m_activity.sku)
                # print(m_activity.goal_name)
                # hours = m_activity.goal_name.quantity/m_activity.sku.manufacture_rate
                style = "background-color: gray;" if activity['status'] == 'orphaned' else "background-color: green;"
                item = {
                    'id': activity['sku'],
                    'group': activity['manufacturing_line'],
                    'manufacturing_lines': allowed_manufacturing_lines,
                    'sku': sku_name,
                    'start': activity['start'],
                    'end': activity['end'],
                    'time_needed': activity['duration'],
                    'style': style,
                    'status': activity['status'],
                    'deadline': deadline,
                    'goal': activity['goal_name'],
                    'content': sku_name
                }
                response['activities'].append(item) 
            # add scheduled_goals and unscheduled_goals
            # format: [{goal_name: {sku_name: {manufacturing_lines, hours_needed}}}]
            enabled_goals = Goal.objects.filter(enable_goal=True)
            for enabled_goal in enabled_goals:
                # if there is no manufacture activity for this goal, skip
                if not Manufacturing_Activity.objects.filter(goal_name=enabled_goal.goalname).exists():
                    continue
                scheduled_goal = {
                    enabled_goal.goalname: {}
                }
                unscheduled_goal = {
                    enabled_goal.goalname: {}
                }
                sku_ids = Manufacture_Goal.objects.filter(name__goalname=enabled_goal.goalname).values_list('sku', flat=True)
                for sku_id in sku_ids:
                    sku = Sku.objects.get(id=sku_id)
                    manufacture_rate = sku.manufacture_rate
                    desired_quantity = Manufacture_Goal.objects.get(sku=sku.id, name__goalname=enabled_goal.goalname).desired_quantity
                    if manufacture_rate == 0:
                        hours_needed = 0
                    else:
                        hours_needed = desired_quantity / manufacture_rate
                    print(hours_needed)
                    sku_lines = set(Sku_To_Ml_Shortname.objects.filter(sku=sku.id).values_list('ml_short_name', flat=True))
                    deadline = Goal.objects.get(goalname=enabled_goal.goalname).deadline
                    if not Manufacturing_Activity.objects.filter(sku=sku.id, goal_name=enabled_goal.goalname).exists():
                        continue
                    elif Manufacturing_Activity.objects.get(sku=sku.id, goal_name=enabled_goal.goalname).status == 'inactive':
                        unscheduled_goal[enabled_goal.goalname][sku.sku_name] = {
                            'manufacturing_lines': list(sku_lines),
                            'hours_needed': math.ceil(hours_needed)
                        }
                        unscheduled_goal[enabled_goal.goalname]['deadline'] = deadline
                    else:
                        scheduled_goal[enabled_goal.goalname][sku.sku_name] = {
                            'manufacturing_lines': list(sku_lines),
                            'hours_needed': math.ceil(hours_needed)
                        }
                        scheduled_goal[enabled_goal.goalname]['deadline'] = deadline
                response['scheduled_goals'].append(scheduled_goal)
                response['unscheduled_goals'].append(unscheduled_goal)
            return Response(response,status = status.HTTP_200_OK)
        except Exception as e: 
            print('exception')
            print(e)
            return Response(status = status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/accounts/login/')
@api_view(['POST'])
def automate_scheduler(request):
    def calculateTime(start_time,duration):
        actual_seconds = 0.0
        duration_seconds = float(duration * 3600)
        start_date_end = datetime.datetime.fromisoformat(str(start_time.date())+'T'+'18:00:00-04:00')
        seconds_gap = start_date_end - start_time;
        # print(seconds_gap.total_seconds())
        if duration_seconds <= seconds_gap.total_seconds():
            actual_seconds += duration_seconds
            return actual_seconds
        duration_seconds -= seconds_gap.total_seconds()
        actual_seconds += seconds_gap.total_seconds()
        if duration_seconds > 0:
            actual_seconds += (3600 * 14)
        days = math.floor(duration_seconds/(3600*10))
        actual_seconds += (days * 3600 * 24)
        duration_seconds -= (days * 3600 * 10)
        actual_seconds += duration_seconds
        return actual_seconds
    def timeCheck(start_time):
        start_date_end = datetime.datetime.fromisoformat(str(start_time.date())+'T'+'18:00:00-04:00')
        if start_time == start_date_end:
            print('true')
            start_time = datetime.datetime.fromisoformat(str(start_time.date()+timedelta(days=1))+'T'+'08:00:00-04:00')
            return start_time
        return start_time
    def findOverlap(start_time, end_time, active_activities,allowed_manufacturing_lines):
        returnDict = {}
        # for ml in allowed_manufacturing_lines:

        return returnDict;
    if(request.method=='POST'):
        try:
            start_date = datetime.datetime.strptime(request.data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(request.data['end_date'], '%Y-%m-%d').date()
            if end_date < start_date:
                post_result = 'error: end_date before start_date'
                return Response(post_result, status = status.HTTP_400_BAD_REQUEST)
            # start_time = datetime.datetime.strptime(request.data['start_date']+' '+'08:00:00', '%Y-%m-%d %H:%M:%S')
            # end_time = datetime.datetime.strptime(request.data['end_date']+' '+'18:00:00', '%Y-%m-%d %H:%M:%S')
            start_time = datetime.datetime.fromisoformat(request.data['start_date']+'T'+'08:00:00-04:00')
            end_time = datetime.datetime.fromisoformat(request.data['end_date']+'T'+'18:00:00-04:00')
            inactive_activities = Manufacturing_Activity.objects.filter(status='inactive', goal_name__deadline__gte=start_date).order_by('goal_name__deadline','duration')
            active_activities = Manufacturing_Activity.objects.filter((Q(status='active')|Q(status='orphaned')), goal_name__deadline__gte=start_date)
            # print(inactive_activities)
            # print(active_activities.filter(start=start_time,manufacturing_line=ml.ml_short_name).exists())
            manufacturing_lines_ordered = {}
            for activity in active_activities: 
                if(not activity.manufacturing_line_id in manufacturing_lines_ordered):
                    manufacturing_lines_ordered[activity.manufacturing_line_id] = []
            for activity in active_activities: 
                manufacturing_lines_ordered[activity.manufacturing_line_id].append(activity)
            print( manufacturing_lines_ordered)
            print(inactive_activities)
            if not inactive_activities:
                post_result = 'error: no activities can be scheduled'
                return Response(post_result, status = status.HTTP_400_BAD_REQUEST)
            # time_needed = calculateTime(start_time,activity['duration'])
            start_t = start_time
            # end_t = start_time
            # add items
            response = {
                'scheduled_activities':[],
                'warning':False
            }
            for m_activity in inactive_activities:
                print("====================")
                activity = ManufacturingActivitySerializer(m_activity).data
                sku_name = Sku.objects.get(id=activity['sku']).sku_name
                allowed_manufacturing_lines = Sku_To_Ml_Shortname.objects.filter(sku=activity['sku']).values_list('ml_short_name', flat=True)
                allowed_manufacturing_lines_list = list(allowed_manufacturing_lines)
                deadline = Goal.objects.get(goalname=activity['goal_name']).deadline
                temp_add_to_line = {}
                for allowed_line in allowed_manufacturing_lines_list: 
                    time_needed_start = calculateTime(start_time,m_activity.duration)
                    if allowed_line in manufacturing_lines_ordered:
                        for i,active_activity in enumerate(manufacturing_lines_ordered[allowed_line]):
                            if(i==0):
                                if(start_time+timedelta(seconds=time_needed_start)<=manufacturing_lines_ordered[allowed_line][i].start):
                                    temp_add_to_line[allowed_line] = {'i':0,'start_time':start_time,'end_time':start_time+timedelta(seconds=time_needed_start)}
                                    break;
                            time_needed = calculateTime(manufacturing_lines_ordered[allowed_line][i].end,m_activity.duration)
                            if(i<len(manufacturing_lines_ordered[allowed_line])-1):
                                if(manufacturing_lines_ordered[allowed_line][i].end+timedelta(seconds=time_needed)<=manufacturing_lines_ordered[allowed_line][i+1].start):
                                    temp_add_to_line[allowed_line] = {'i':i+1, 'start_time':manufacturing_lines_ordered[allowed_line][i].end,'end_time':manufacturing_lines_ordered[allowed_line][i].end+timedelta(seconds=time_needed)}
                            else: 
                                if(manufacturing_lines_ordered[allowed_line][i].end+timedelta(seconds=time_needed)<=end_time):
                                    temp_add_to_line[allowed_line] = {'i':i+1, 'start_time':manufacturing_lines_ordered[allowed_line][i].end,'end_time':manufacturing_lines_ordered[allowed_line][i].end+timedelta(seconds=time_needed)}
                                    print(temp_add_to_line)
                    else: 
                        if(start_time+timedelta(seconds=time_needed_start)<=end_time):
                            temp_add_to_line[allowed_line] = {'i':0, 'start_time':start_time,'end_time':start_time+timedelta(seconds=time_needed_start)}
                print(temp_add_to_line)
                if(not temp_add_to_line):
                   response['warning']=True
                earliest_time = None
                add_to_line = None

                for line in temp_add_to_line:
                    if(earliest_time == None):
                        add_to_line = line
                        earliest_time = temp_add_to_line[line]['start_time']
                    else: 
                        if(earliest_time > temp_add_to_line[line]['start_time']):
                            add_to_line = line
                            earliest_time = temp_add_to_line[line]['start_time']
                if(add_to_line!=None):
                    print("FINAL ADDED LINE BELOW:")
                    print(temp_add_to_line[add_to_line])
                

                if(add_to_line in manufacturing_lines_ordered):
                    m_activity.start = temp_add_to_line[add_to_line]['start_time']
                    m_activity.end = temp_add_to_line[add_to_line]['end_time']
                    manufacturing_lines_ordered[add_to_line].insert(temp_add_to_line[add_to_line]['i'],m_activity)
                else: 
                    m_activity.start = temp_add_to_line[add_to_line]['start_time']
                    m_activity.end = temp_add_to_line[add_to_line]['end_time']
                    manufacturing_lines_ordered[add_to_line] = []
                    manufacturing_lines_ordered[add_to_line].append(m_activity)
                print(manufacturing_lines_ordered)
                response['scheduled_activities'].append({'start':temp_add_to_line[add_to_line]['start_time'],'end':temp_add_to_line[add_to_line]['end_time'],'sku-id':m_activity.sku_id,'sku-name':sku_name,'goal-name':m_activity.goal_name_id})
                print("************************")
                # for ml in allowed_manufacturing_lines:
                #     print(ml)
                #     if active_activities.filter(start=start_t,manufacturing_line=ml).exists():
                #         active_activity = active_activities.get(start=start_time,manufacturing_line=ml)


              
                # serializer = ManufacturingActivitySerializer(m_activity,{'start':start_t,'end':end_t},partial=True)
                # if(serializer.is_valid()):
                #     serializer.save()  
            return Response(response,status = status.HTTP_200_OK)
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/accounts/login/')
@api_view(['POST'])
def schedule_data(request):
    if(request.method=='POST'):
        try:
            activities = Manufacturing_Activity.objects.all()
        except Exception as e: 
            return Response(status = status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/accounts/login/')
@api_view(['GET','POST'])
def get_sales_report(request):
    try:
        scrapyd = ScrapydAPI('http://152.3.53.19:6800')
        task_id = scrapyd.schedule('default', 'sales')
        result = {
            'task_id': task_id
        }
        return Response(result, status = status.HTTP_200_OK)
    except Exception as e: 
        print('exception in get_sales_report:')
        print(e)
        return Response(status = status.HTTP_400_BAD_REQUEST)

# Update Manufacturing Activity based on manufacturing rate and desired quantity
def update_activity():
    try:
        for manufacture_activity in Manufacturing_Activity.objects.all():
            goal = Goal.objects.get(goalname = manufacture_activity.goal_name.goalname)
            # update status
            update_status = manufacture_activity.status
            if goal.enable_goal == False and manufacture_activity.status == 'active':
                update_status = 'orphaned'
            elif goal.enable_goal == True and manufacture_activity.status == 'orphaned':
                update_status = 'active'
            # update duration
            manufacture_rate = Sku.objects.get(id=manufacture_activity.sku.id).manufacture_rate
            desired_quantity = Manufacture_Goal.objects.get(
                sku=manufacture_activity.sku.id, 
                name__goalname=manufacture_activity.goal_name.goalname).desired_quantity
            if manufacture_rate == 0:
                duration = 0
            else:
                duration = desired_quantity / manufacture_rate
            update_fields = {
                'status': update_status,
                'duration': math.ceil(duration),
            }
            print('update_fields')
            print(update_fields)
            serializer = ManufacturingActivitySerializer(manufacture_activity, data=update_fields, partial=True)
            if(serializer.is_valid()):
                serializer.save()
            else:
                print(serializer.errors)
    except Exception as e: 
        print(e)

