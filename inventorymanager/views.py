from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from reportlab.pdfgen import canvas
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from django.db import transaction

import csv
import io

# Create your views here.
@login_required(login_url='/accounts/login/')
def index(request):
	return render(request,'home.html')

@login_required(login_url='/accounts/login/')
def ingredient(request):
	return render(request, "ingredient.html")

@login_required(login_url='/accounts/login/')
def sku(request):
	return render(request, "sku.html")
	
@login_required(login_url='/accounts/login/')
def manufacture_goal(request,goalid):
	return render(request, "manufacturing.html",{'goalid':goalid})

@login_required(login_url='/accounts/login/')
def ingredients_to_sku(request,skuid):
	return render(request, "ingredients_to_sku.html",{'skuid':skuid})

@login_required(login_url='/accounts/login/')
def skus_to_ingredients(request,ingredientid):
	return render(request, "skus_to_ingredient.html",{'ingredientid':ingredientid})

@login_required(login_url='/accounts/login/')
def product_line(request):
	return render(request, "product_line.html")

@login_required(login_url='/accounts/login/')
def goal(request):
	return render(request, "goal.html")

# @login_required(login_url='/accounts/login/')
# def goal(request):
# 	return render(request, "calculate.html",{'goalid':goalid})
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
		csv_file = request.data['file']
		errors, warnings = self.save(csv_file)
		post_result = {'errors': errors, 'warnings': warnings}
		if errors != []:
			return Response(post_result, status.HTTP_400_BAD_REQUEST)
		return Response(post_result, status.HTTP_201_CREATED)

		# file_serializer = IngredientFileSerializer(data=request.data)
		# if file_serializer.is_valid():
			# file_serializer.save()
			# Use self.method() to access the function inside the same class...
			# https://stackoverflow.com/questions/24813740/python-error-cannot-access-function-in-class 
		# 	self.validate(request.data['file'])
		# 	return Response(file_serializer.data, status.HTTP_201_CREATED)
		# else:
		# 	return Response(file_serializer.errors, status.HTTP_400_BAD_REQUEST)

	# https://stackoverflow.com/questions/40663168/processing-an-uploaded-file-using-django
	# return [errors], [warnings]
	@transaction.atomic
	def save(self, csv_file):
		errors = []
		warnings = []
		# https://docs.djangoproject.com/en/1.9/topics/db/transactions/#savepoint-rollback
		transaction_savepoint = transaction.savepoint()
		with open(csv_file.name) as f:
			reader = csv.DictReader(f)
			header_val_error, _ = self.validate_header(reader.fieldnames)
			if header_val_error:
				errors.append(header_val_error)
			for ingr_dict in reader:
				ingr_val_error, ingr_val_warning = self.validate_ingredient(ingr_dict)
				if ingr_val_warning:
					warnings.append(ingr_val_warning)
				if ingr_val_error:
					errors.append(ingr_val_error)
					break
				ingredient = Ingredient(id=ingr_dict['Ingr#'],
										ingredient_name=ingr_dict['Name'].lower(), 
										description=ingr_dict['Vendor Info'],
										package_size=ingr_dict['Size'],
										cpp=ingr_dict['Cost'],
										comment=ingr_dict['Comment'])
				# save without commit, as later validation might fail 
				ingredient.save()
		if errors != []:
			transaction.savepoint_rollback(transaction_savepoint)
		else:
			transaction.savepoint_commit(transaction_savepoint)
		return errors, warnings
	
	def validate_header(self, headers):
		if headers != ['Ingr#','Name','Vendor Info','Size','Cost','Comment']:
			return 'File headers not compliant to standard', ''
		return '', ''

	# validation conforms to https://piazza.com/class/jpvlvyxg51d1nc?cid=52
	def validate_ingredient(self, ingredient_dict):
		error = ''
		warning = ''
		# if ingredient with same name exists, only update if id matches
		if Ingredient.objects.filter(ingredient_name=ingredient_dict['Name']).exists():
			same_name_ingr = Ingredient.objects.get(ingredient_name=ingredient_dict['Name'])
			if same_name_ingr.pk != int(ingredient_dict['Ingr#']):
				error = 'Ambiguous record for %s' % same_name_ingr.ingredient_name
			else:
				# update other fields
				warning = 'Update fields for %s' % same_name_ingr.ingredient_name
		else:
			# check if object with same id exists
			if Ingredient.objects.filter(pk=ingredient_dict['Ingr#']).exists():
				# overwrite existing object
				warning = 'Overwrite object with id %s' % ingredient_dict['Ingr#']
		return error, warning

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
                # for ingredient in Ingredient.objects.all():
                for ingredient in ingredients:
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
