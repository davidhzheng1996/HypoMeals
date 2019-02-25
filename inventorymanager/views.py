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
from datetime import date

import csv
import io

# Create your views here.
@login_required(login_url='/accounts/login/')
def index(request):
	return render(request,'home.html')
	
def netid(request):
	return render(request,'netid.html')


@login_required(login_url='/accounts/login/')
def ingredient(request):
	return render(request, "ingredient.html")

@login_required(login_url='/accounts/login/')
def sku(request):
	return render(request, "sku.html")

@login_required(login_url='/accounts/login/')
def formula(request):
	return render(request, "formula.html")
	
@login_required(login_url='/accounts/login/')
def manufacture_goal(request,goalid):
	return render(request, "manufacturing.html",{'goalid':goalid})

@login_required(login_url='/accounts/login/')
def scheduler(request):
	return render(request,"scheduler.html")

# @login_required(login_url='/accounts/login/')
# def ingredients_to_sku(request,skuid):
# 	return render(request, "ingredients_to_sku.html",{'skuid':skuid})

@login_required(login_url='/accounts/login/')
def formula_to_sku(request,formulaid):
	return render(request, "formula_to_sku.html",{'formulaid':formulaid})

@login_required(login_url='/accounts/login/')
def skus_to_formula(request,formulaid):
	return render(request, "skus_to_formula.html",{'formulaid':formulaid})

# @login_required(login_url='/accounts/login/')
# def formula_to_sku(request,skuid):
# 	return render(request, "formula_to_sku.html",{'formulaid':formulaid})

@login_required(login_url='/accounts/login/')
def ingredients_to_formula(request,formulaid):
	return render(request, "ingredients_to_formula.html",{'formulaid':formulaid})

@login_required(login_url='/accounts/login/')
def skus_to_ingredients(request,ingredientid):
	return render(request, "skus_to_ingredient.html",{'ingredientid':ingredientid})

@login_required(login_url='/accounts/login/')
def product_line(request):
	return render(request, "product_line.html")

@login_required(login_url='/accounts/login/')
def manufacture_line(request):
	return render(request, "manufacture_line.html")

@login_required(login_url='/accounts/login/')
def goal(request):
	return render(request, "goal.html")

@login_required(login_url='/accounts/login')
def calculate_goal(request,goalid):
	return render(request,"calculate.html",{'goalid':goalid})
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
				return errors, warnings
			for ingr_dict in reader:
				ingr_val_error, ingr_val_warning = self.validate_ingredient(ingr_dict)
				unit_error = self.validate_unit(ingr_dict)
				if ingr_val_warning:
					warnings.append(ingr_val_warning)
				if ingr_val_error:
					errors.append(ingr_val_error)
					break
				if not unit_error:
					errors.append("package size unit incorrect for %s" % ingr_dict['Name'])
					break;
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

	def validate_unit(self, ingredient_dict):
		units = ['lb', 'pound', 'oz', 'ounce', 'ton', 'g', 'gram', 'kg', 'kilogram', 'floz', 'fluidounce', 'pt', 'pint', 'qt', 'quart', 'gal', 'gallon', 'ml', 'milliliter', 'l', 'liter', 'ct', 'count']
		size = ingredient_dict['Size']
		size_unit = re.sub(r'\d*\.?\d+', '', size)
		size_unit = size_unit.replace(' ', '').replace('.','').lower()
		if len(size_unit) > 1 and (size_unit[len(size_unit)-1]=='s'):
			size_unit = size_unit[:-1]
		if size_unit not in units:
			return False
		return True

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
		csv_file = request.data['file']
		errors, warnings = self.save(csv_file)
		post_result = {'errors': errors, 'warnings': warnings}
		if errors != []:
			return Response(post_result, status.HTTP_400_BAD_REQUEST)
		return Response(post_result, status.HTTP_201_CREATED)
		
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
				return errors, warnings
			for sku_dict in reader:
				val_error, val_warning = self.validate_sku(sku_dict)
				if val_warning:
					warnings.append(val_warning)
				if val_error:
					errors.append(val_error)
					break
				product_line = Product_Line.objects.get(product_line_name=sku_dict['PL Name'])
				formula = Formula.objects.get(id=sku_dict['Formula#'])
				if not sku_dict['SKU#']:
					default_id = 0
				else:
					default_id = sku_dict['SKU#']
				sku = Sku(
						id=default_id,
						productline=product_line,
						caseupc=sku_dict['Case UPC'],
						unitupc=sku_dict['Unit UPC'],
						sku_name=sku_dict['Name'],
						count=sku_dict['Count per case'],
						unit_size=sku_dict['Unit size'],
						formula=formula,
						formula_scale_factor=sku_dict['Formula factor'],
						manufacture_rate=sku_dict['Rate'],
						comment=sku_dict['Comment'])
				serializer = SkuSerializer(data=sku)
				if serializer.is_valid():
					serializer.save()
				# save all manufacturing lines associated with sku
				ml_shortnames = sku_dict['ML Shortnames'].strip('"').split(',')
				for ml_shortname in ml_shortnames:
					if Sku_To_Ml_Shortname.objects.filter(sku=sku_dict['SKU#'],ml_short_name=ml_shortname).exists():
						continue
					sku_object = Sku.objects.get(id=sku_dict['SKU#'])
					ml_short_name_object = Manufacture_line.objects.get(ml_short_name=ml_shortname)
					sku2ml = Sku_To_Ml_Shortname(sku=sku_object,ml_short_name=ml_short_name_object)
					sku2ml.save()

		if errors != []:
			transaction.savepoint_rollback(transaction_savepoint)
		else:
			transaction.savepoint_commit(transaction_savepoint)
		return errors, warnings

	def validate_header(self, headers):
		if headers != ['SKU#','Name','Case UPC','Unit UPC','Unit size','Count per case','PL Name','Formula#','Formula factor', 'ML Shortnames', 'Rate','Comment']:
			return 'File headers not compliant to standard', ''
		return '', ''

	# validation conforms to https://piazza.com/class/jpvlvyxg51d1nc?cid=52
	def validate_sku(self, sku_dict):
		error = ''
		warning = ''
		case_upc = self.validate_case_upc(sku_dict)
		unit_upc = self.validate_unit_upc(sku_dict)
		# if ingredient with same name exists, only update if id matches
		if Sku.objects.filter(sku_name=sku_dict['Name']).exists():
			same_name_sku = Sku.objects.get(sku_name=sku_dict['Name'])
			if same_name_sku.pk != int(sku_dict['SKU#']):
				error = 'Ambiguous record for %s' % same_name_sku.sku_name
			else:
				# update other fields
				warning = 'Update fields for %s' % same_name_sku.sku_name
		elif not case_upc:
			error = 'Case UPC invalid for %s' % sku_dict['Name']
		elif not unit_upc:
			 error = 'Unit UPC invalid for %s' % sku_dict['Name']
		else:
			# check if object with same id exists
			if Sku.objects.filter(pk=sku_dict['SKU#']).exists():
				# overwrite existing object
				warning = 'Overwrite object with id %s' % sku_dict['Ingr#']
		# check if product line exists
		product_line_name = sku_dict['PL Name']
		if not Product_Line.objects.filter(product_line_name=product_line_name).exists():
			error = 'No product line named %s' % product_line_name
		# check if manufacturing lines exist 
		ml_shortnames = sku_dict['ML Shortnames'].strip('"').split(',')
		for ml_shortname in ml_shortnames:
			if not Manufacture_line.objects.filter(ml_short_name=ml_shortname).exists():
				error = 'No manufacturing line named %s' % ml_shortname
				break
		return error, warning

	def validate_case_upc(self, sku_dict):
		if sku_dict['Case UPC'][0] == '2' or sku_dict['Case UPC'][0] == '3' or sku_dict['Case UPC'][0] == '4' or sku_dict['Case UPC'][0] == '5':
			return False
		odds = int(sku_dict['Case UPC'][0]) + int(sku_dict['Case UPC'][2]) + int(sku_dict['Case UPC'][4]) + int(sku_dict['Case UPC'][6]) + int(sku_dict['Case UPC'][8])+ int(sku_dict['Case UPC'][10])
		evens = int(sku_dict['Case UPC'][1]) + int(sku_dict['Case UPC'][3]) + int(sku_dict['Case UPC'][5]) + int(sku_dict['Case UPC'][7]) + int(sku_dict['Case UPC'][9])
		sumNum = odds*3 + evens
		# if sumNum % 10 == 0 and int(sku_dict['Case UPC'][11]) != 0:
		# 	return False
		# else:
		# 	check = 10 - (sumNum % 10)
		# 	if int(sku_dict['Case UPC'][11]) != check:
		# 		return False

		return True;

	def validate_unit_upc(self, sku_dict):
		if sku_dict['Unit UPC'][0] == '2' or sku_dict['Unit UPC'][0] == '3' or sku_dict['Unit UPC'][0] == '4' or sku_dict['Unit UPC'][0] == '5':
			return False
		odds = int(sku_dict['Unit UPC'][0]) + int(sku_dict['Unit UPC'][2]) + int(sku_dict['Unit UPC'][4]) + int(sku_dict['Unit UPC'][6]) + int(sku_dict['Unit UPC'][8])+ int(sku_dict['Unit UPC'][10])
		odds = odds*3
		evens = int(sku_dict['Unit UPC'][1]) + int(sku_dict['Unit UPC'][3]) + int(sku_dict['Unit UPC'][5]) + int(sku_dict['Unit UPC'][7]) + int(sku_dict['Unit UPC'][9])
		sumNum = odds + evens
		# if sumNum % 10 == 0 and int(sku_dict['Unit UPC'][11]) != 0:
		# 	return False
		# else:
		# 	check = 10 - (sumNum % 10)
		# 	if int(sku_dict['Unit UPC'][11]) != check:
		# 		return False
		return True;


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


class FormulaImportView(APIView):
	# available parsers: https://www.django-rest-framework.org/api-guide/parsers/ 
	# file sent should be in FormData
	parser_classes = (MultiPartParser, FormParser)
	def post(self, request, *args, **kwargs):
		csv_file = request.data['file']
		errors, warnings = self.save(csv_file)
		post_result = {'errors': errors, 'warnings': warnings}
		if errors != []:
			return Response(post_result, status.HTTP_400_BAD_REQUEST)
		return Response(post_result, status.HTTP_201_CREATED)
		
	@transaction.atomic
	def save(self, formula_file):
		errors = []
		warnings = []
		# https://docs.djangoproject.com/en/1.9/topics/db/transactions/#savepoint-rollback
		transaction_savepoint = transaction.savepoint()
		with open(formula_file.name) as f:
			reader = csv.DictReader(f)
			header_val_error, _ = self.validate_header(reader.fieldnames)
			if header_val_error:
				errors.append(header_val_error)
				return errors, warnings
			for formula_dict in reader:
				val_error, val_warning = self.validate_formula(formula_dict)
				unit_error = self.validate_unit(formula_dict)
				if val_warning:
					warnings.append(val_warning)
				if val_error:
					errors.append(val_error)
					break
				if not unit_error:
					errors.append("package size unit incorrect for %s" % formula_dict['Name'])
					break;
				# store formula first if not exist 
				if not Formula.objects.filter(formula_name=formula_dict['Name'], id=formula_dict['Formula#']).exists():
					formula = Formula(formula_name=formula_dict['Name'],
									  id=formula_dict['Formula#'],
									  comment=formula_dict['Comment'])
					formula.save()
				# add to Formula_To_Ingredients table if not exist
				formula = Formula.objects.get(formula_name=formula_dict['Name'])
				ingr = Ingredient.objects.get(id=formula_dict['Ingr#'])
				if not Formula_To_Ingredients.objects.filter(formula=formula.id, ig=ingr.id).exists():
					formula_to_ingr = Formula_To_Ingredients(
						formula=formula,
						ig=ingr,
						quantity=formula_dict['Quantity'])
					# save without commit, as later validation might fail 
					formula_to_ingr.save()
		if errors != []:
			transaction.savepoint_rollback(transaction_savepoint)
		else:
			transaction.savepoint_commit(transaction_savepoint)
		return errors, warnings

	def validate_header(self, headers):
		if headers != ['Formula#','Name','Ingr#','Quantity','Comment']:
			return 'File headers not compliant to standard', ''
		return '', ''

	# validation conforms to https://piazza.com/class/jpvlvyxg51d1nc?cid=52
	def validate_formula(self, formula_dict):
		error = ''
		warning = ''
		if not Ingredient.objects.filter(id=formula_dict['Ingr#']).exists():
			error = 'No ingredient with id %s' % formula_dict['Ingr#']
		# check if formula exist
		# if formula name exists but a different id, error
		if Formula.objects.filter(formula_name=formula_dict['Name']).exists():
			same_name_formua = Formula.objects.get(formula_name=formula_dict['Name'])
			if same_name_formua.pk != int(formula_dict['Formula#']):
				error = 'Ambiguous record for %s' % same_name_formua.formula_name
			else:
				# update other fields
				if same_name_formua.formula_name != formula_dict['Name']:
					warning = 'Update fields for %s' % same_name_formua.formula_name
		# if formula id exists but a different name, replace
		elif Formula.objects.filter(pk=formula_dict['Formula#']).exists():
				# overwrite existing object
				warning = 'Overwrite object with id %s' % formula_dict['Formula#']
		return error, warning

	def validate_unit(self, formula_dict):
		ingr = Ingredient.objects.get(id=formula_dict['Ingr#'])
		package_size = ingr.package_size
		units = ['lb', 'pound', 'oz', 'ounce', 'ton', 'g', 'gram', 'kg', 'kilogram', 'floz', 'fluidounce', 'pt', 'pint', 'qt', 'quart', 'gal', 'gallon', 'ml', 'milliliter', 'l', 'liter', 'ct', 'count']
		mass = ['lb', 'pound', 'oz', 'ounce', 'ton', 'g', 'gram', 'kg', 'kilogram']
		volume = ['floz', 'fluidounce', 'pt', 'pint', 'qt', 'quart', 'gal', 'gallon', 'ml', 'milliliter', 'l', 'liter']
		count = ['ct', 'count']
		size = formula_dict['Quantity']
		size_unit = re.sub(r'\d*\.?\d+', '', size)
		size_unit = size_unit.replace(' ', '').replace('.','').lower()
		package_size_unit = re.sub(r'\d*\.?\d+', '', package_size)
		package_size_unit = package_size_unit.replace(' ', '').replace('.','').lower()
		if len(size_unit) > 1 and (size_unit[len(size_unit)-1]=='s'):
			size_unit = size_unit[:-1]
		if size_unit not in units:
			return False
		if len(package_size_unit) > 1 and (package_size_unit[len(package_size_unit)-1]=='s'):
			package_size_unit = package_size_unit[:-1]
		if package_size_unit in mass and size_unit not in mass:
			return False
		if package_size_unit in volume and size_unit not in volume:
			return False
		if package_size_unit in count and size_unit not in count:
			return False

		return True

class FormulaExportView(APIView):
	def get(self, request, *args, **kwargs):
		# https://docs.djangoproject.com/en/2.1/howto/outputting-csv/
		# export all Ingredients into a csv file
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = "attachment; filename=\"skus.csv\""
		writer = csv.writer(response)
		# Formula#,Name,Ingr#,Quantity,Comment
		# for each formula, pull out all associated ingredients
		header = ["Formula#","Name","Ingr#","Quantity","Comment"]
		writer.writerow(header)
		for formula in Formula.objects.all():
			formula2ingrs = Formula_To_Ingredients.objects.filter(formula=formula.id)
			for formula2ingr in formula2ingrs:
				formula_row = [
					formula.id,
					formula.formula_name,
					formula2ingr.ig.id,
					formula2ingr.quantity,
					formula.comment
				]
				writer.writerow(formula_row)
		return response

class ProductLineImportView(APIView):
	# available parsers: https://www.django-rest-framework.org/api-guide/parsers/ 
	# file sent should be in FormData
	parser_classes = (MultiPartParser, FormParser)
	def post(self, request, *args, **kwargs):
		csv_file = request.data['file']
		errors, warnings = self.save(csv_file)
		post_result = {'errors': errors, 'warnings': warnings}
		if errors != []:
			return Response(post_result, status.HTTP_400_BAD_REQUEST)
		return Response(post_result, status.HTTP_201_CREATED)
		
	@transaction.atomic
	def save(self, product_line_file):
		errors = []
		warnings = []
		# https://docs.djangoproject.com/en/1.9/topics/db/transactions/#savepoint-rollback
		transaction_savepoint = transaction.savepoint()
		with open(product_line_file.name) as f:
			reader = csv.DictReader(f)
			header_val_error, _ = self.validate_header(reader.fieldnames)
			if header_val_error:
				errors.append(header_val_error)
				return errors, warnings
			for product_line_dict in reader:
				val_error, val_warning = self.validate_formula(product_line_dict)
				if val_warning:
					warnings.append(val_warning)
				if val_error:
					errors.append(val_error)
					break
				if not Product_Line.objects.filter(product_line_name=product_line_dict['Name']).exists():
					product_line = Product_Line(product_line_name=product_line_dict['Name'])
					product_line.save()
		if errors != []:
			transaction.savepoint_rollback(transaction_savepoint)
		else:
			transaction.savepoint_commit(transaction_savepoint)
		return errors, warnings

	def validate_header(self, headers):
		if headers != ['Name']:
			return 'File headers not compliant to standard', ''
		return '', ''

	# validation conforms to https://piazza.com/class/jpvlvyxg51d1nc?cid=52
	def validate_formula(self, product_line_dict):
		error = ''
		warning = ''
		if Product_Line.objects.filter(product_line_name=product_line_dict['Name']).exists():
			warning = 'Exsiting product line: %s' % product_line_dict['Name']
		return error, warning