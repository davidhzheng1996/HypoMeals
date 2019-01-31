from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *

import csv

# Create your views here.
@login_required(login_url='/accounts/login/')
def index(request):
	return render(request,'home.html')

@login_required(login_url='/accounts/login/')
def ingredient(request):
	return render(request, "ingredient.html")
# def ingredient(request,
#     template='ingredient.html'):
#     context = {
#         'ingredient': Ingredient.objects.all(),
#     }
#     return render(request, template, context)

@login_required(login_url='/accounts/login/')
def sku(request):
	return render(request, "sku.html")
	
@login_required(login_url='/accounts/login/')
def manufacture_goal(request):
	return render(request, "manufacturing.html")

@login_required(login_url='/accounts/login/')
def product_line(request):
	return render(request, "product_line.html")
# https://blog.vivekshukla.xyz/uploading-file-using-api-django-rest-framework/
# https://www.django-rest-framework.org/api-guide/views/
# APIView is specific for handling REST API requests. User need to Explicitly describe  
# the logic for post, get, delete, etc. If not described, action is not allowed. 
# We do not use ViewSet for IngredientFile because user should not be able issue GET or
# DELETE requests for IngredientFile 
# TODO Should we save the imported file at all?
class IngredientImportView(APIView):
	# available parsers: https://www.django-rest-framework.org/api-guide/parsers/ 
	# file sent should be in FormData
	parser_classes = (MultiPartParser, FormParser)
	def post(self, request, *args, **kwargs):
		# https://stackoverflow.com/questions/28545553/django-rest-frameworks-request-post-vs-request-data
		# request.data is more flexible than request.FILES
		file_serializer = IngredientFileSerializer(data=request.data)
		if file_serializer.is_valid():
			file_serializer.save()
			# Use self.method() to access the function inside the same class...
			# https://stackoverflow.com/questions/24813740/python-error-cannot-access-function-in-class 
			self.process_file(request.data['file'])
			return Response(file_serializer.data, status.HTTP_201_CREATED)
		else:
			return Response(file_serializer.errors, status.HTTP_400_BAD_REQUEST)
	# https://stackoverflow.com/questions/40663168/processing-an-uploaded-file-using-django
	def process_file(self, csv_file):
		with open(csv_file.name) as f:
			reader = csv.DictReader(f)
			for row in reader:
				ingredient = Ingredient(ingredient_name=row['ingredient_name'], 
									description=row['description'],
									package_size=row['package_size'],
									cpp=row['cpp'],
									comment=row['comment'])
				ingredient.save()

class IngredientExportView(APIView):
        def get(self, request, *args, **kwargs):
                # https://docs.djangoproject.com/en/2.1/howto/outputting-csv/
                # export all Ingredients into a csv file
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = "attachment; filename=\"ingredients.csv\""

                writer = csv.writer(response)
                # https://stackoverflow.com/questions/15029666/exporting-items-from-a-model-to-csv-django-python
                ingredient_fields = Ingredient._meta.fields
                field_row = [field.name for field in ingredient_fields]
                writer.writerow(field_row)
                for ingredient in Ingredient.objects.all():
                        ingredient_row = []
                        for field in Ingredient._meta.fields:
                                ingredient_row.append(getattr(ingredient, field.name))
                        writer.writerow(ingredient_row)
                return response

class SkuImportView(APIView):
	# available parsers: https://www.django-rest-framework.org/api-guide/parsers/ 
	# file sent should be in FormData
	parser_classes = (MultiPartParser, FormParser)
	def post(self, request, *args, **kwargs):
		# https://stackoverflow.com/questions/28545553/django-rest-frameworks-request-post-vs-request-data
		# request.data is more flexible than request.FILES
		file_serializer = SkuFileSerializer(data=request.data)
		if file_serializer.is_valid():
			file_serializer.save()
			# Use self.method() to access the function inside the same class...
			# https://stackoverflow.com/questions/24813740/python-error-cannot-access-function-in-class 
			self.process_file(request.data['file'])
			return Response(file_serializer.data, status.HTTP_201_CREATED)
		else:
			return Response(file_serializer.errors, status.HTTP_400_BAD_REQUEST)
	# https://stackoverflow.com/questions/40663168/processing-an-uploaded-file-using-django
	def process_file(self, csv_file):
		print(csv_file)
		with open(csv_file.name) as f:
			reader = csv.DictReader(f)
			for row in reader:
				print(row)
				sku = Sku(productline=row['productline'],
						caseupc=row['caseupc'],
						unitupc=row['unitupc'],
						sku_name=row['sku_name'],
						count=row['count'],
						unit_size=row['unit_size'],
						tuples=row['tuples'],
						comment=row['comment'])
				sku.save()

class SkuExportView(APIView):
        def get(self, request, *args, **kwargs):
                # https://docs.djangoproject.com/en/2.1/howto/outputting-csv/
                # export all Ingredients into a csv file
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = "attachment; filename=\"skus.csv\""

                writer = csv.writer(response)
                # https://stackoverflow.com/questions/15029666/exporting-items-from-a-model-to-csv-django-python
                sku_fields = Sku._meta.fields
                field_row = [field.name for field in sku_fields]
                writer.writerow(field_row)
                for sku in Sku.objects.all():
                        sku_row = []
                        for field in Sku._meta.fields:
                                sku_row.append(getattr(sku, field.name))
                        writer.writerow(sku_row)
                return response
