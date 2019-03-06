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
import re
import os

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

@login_required(login_url='/accounts/login/')
def ingredients_to_sku(request,skuid):
	return render(request, "ingredients_to_sku.html",{'skuid':skuid})

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
def skus_to_ingredient(request,ingredientid):
	return render(request, "skus_to_ingredient.html",{'ingredientid':ingredientid})

@login_required(login_url='/accounts/login/')
def product_line(request):
	return render(request, "product_line.html")

@login_required(login_url='/accounts/login/')
def manufacture_line(request):
	return render(request, "manufacture_line.html")

@login_required(login_url='/accounts/login/')
def scheduler_report(request):
	return render(request, "manufacture_report.html")

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
		try:
			csv_file = request.data['data']
			# print(csv_file)
			directory = os.getcwd()

			# response = HttpResponse(content_type='text/csv')
			# response['Content-Disposition'] = "attachment; filename=\"product_line.csv\""f
			# f = io.StringIO(csv_file)
			# csv_file = csv_file.split('\n')
			# headers =csv_file[0].split(',')
			# writer = csv.writer(open(directory+"/outputIngredient.csv", 'w'))
			# writer.writerow(headers)
			# print(len(csv_file))
			# for i in range(1, len(csv_file)):
			# 	# if(',' in csv_file[i]):
			# 	row = csv_file[i].split(',')
			# 	if(len(row)<len(headers)):
			# 		print('hi')
			# 		prevRow = csv_file[i-1].split(',')
			# 		print(prevRow[len(headers)-1])
			# 		prevRow[len(headers)-1]+ " " + row
			# 		print(prevRow)
			# 		continue
			# 	print(row)
			# 	# row1=''
			# 	# for i in range(0, len(headers)):
			# 	# 	row1 = row[i]+','
			# 	# print(row1)
			# 	writer.writerow(row)
			# reader = csv.reader(f, delimiter=',')
			# for row in reader:
			# 	print('\t'.join(row))
			# print(f)
			errors, warnings = self.save(csv_file)
			post_result = {'errors': errors, 'warnings': warnings}
			if errors != []:
				return Response(post_result, status.HTTP_400_BAD_REQUEST)
			return Response(post_result, status.HTTP_201_CREATED)
		except Exception as e: 
			return Response(status = status.HTTP_400_BAD_REQUEST)
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
		f = io.StringIO(csv_file)
		reader = csv.reader(f, delimiter=',')
		first = True
		ingr_dict = {}
		for ingr_row in reader:
			if first:
				header = ingr_row
				header_val_error, _ = self.validate_header(header)
				if header_val_error:
					errors.append(header_val_error)
					return errors, warnings
				first = False
				continue
			else:
				# {Ingr#: ingr, Name: ingr_name, etc.} for each ingredient 
				for idx, ele in enumerate(ingr_row):
					ingr_dict[header[idx]] = ele
				if not ingr_dict['Ingr#']:
					if not Ingredient.objects.all():
						default_id = 1
					else:
						default_id =  Ingredient.objects.all().order_by("-id")[0].id + 1
				else:
					try:
						int(ingr_dict['Ingr#'])
					except ValueError:
						errors.append(ingr_dict['Ingr#'] + " is not a number,")
						continue
					default_id = int(ingr_dict['Ingr#'])
				ingr_val_error, ingr_val_warning = self.validate_ingredient(ingr_dict, default_id)
				unit_error = self.validate_unit(ingr_dict)
				if ingr_val_warning:
					warnings.append(ingr_val_warning)
				if ingr_val_error:
					errors.append(ingr_val_error)
					break
				if not unit_error:
					errors.append("package size unit incorrect for %s," % ingr_dict['Name'])
					break
				if not Ingredient.objects.filter(id=default_id).exists():
					serializer = IngredientSerializer(data={'id':default_id,'ingredient_name':ingr_dict['Name'].lower(),'description':ingr_dict['Vendor Info'],'package_size':ingr_dict['Size'],'cpp':ingr_dict['Cost'],'comment':ingr_dict['Comment']})
					# print(serializer.data)
					if(serializer.is_valid()):
						serializer.save()
					else:
						for error in serializer.errors.values():
							errors.append(error)
						break
				else:
					ingr = Ingredient.objects.get(id=default_id)
					s = IngredientSerializer(ingr)
					s_data = s.data
					ingr.delete()
					s_data['ingredient_name']=ingr_dict['Name'].lower()
					s_data['description']=ingr_dict['Vendor Info']
					s_data['package_size']=ingr_dict['Size']
					s_data['cpp']=ingr_dict['Cost']
					s_data['comment']=ingr_dict['Comment']
					serializer = IngredientSerializer(data=s_data)
					# print(serializer)
					if(serializer.is_valid()):
						serializer.save()
					else:
						for error in serializer.errors.values():
							errors.append(error)
						break
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
	def validate_ingredient(self, ingredient_dict, default_id):
		error = ''
		warning = ''
		# if ingredient with same name exists, only update if id matches
		# print(Ingredient.objects.get(ingredient_name=ingredient_dict['Name']).exists())
		print(ingredient_dict['Name'])
		if Ingredient.objects.filter(ingredient_name=ingredient_dict['Name']).exists():
			same_name_ingr = Ingredient.objects.get(ingredient_name=ingredient_dict['Name'])
			print(same_name_ingr)
			# print(Ingredient.objects.get(ingredient_name=ingredient_dict['Name']))
			if same_name_ingr.pk != default_id:
				print('hit')
				error = 'Ambiguous record for %s,' % same_name_ingr.ingredient_name
			else:
				# update other fields
				warning = 'Update fields for %s,' % same_name_ingr.ingredient_name
		else:
			# check if object with same id exists
			if Ingredient.objects.filter(pk=default_id).exists():
				# overwrite existing object
				warning = 'Overwrite object with id %s' % str(default_id)
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
		try:
			csv_file = request.data['data']
			errors, warnings = self.save(csv_file)
			post_result = {'errors': errors, 'warnings': warnings}
			if errors != []:
				return Response(post_result, status.HTTP_400_BAD_REQUEST)
			return Response(post_result, status.HTTP_201_CREATED)
		except Exception as e: 
			return Response(status = status.HTTP_400_BAD_REQUEST)
		
		
	@transaction.atomic
	def save(self, csv_file):
		errors = []
		warnings = []
		# https://docs.djangoproject.com/en/1.9/topics/db/transactions/#savepoint-rollback
		transaction_savepoint = transaction.savepoint()
		f = io.StringIO(csv_file)
		reader = csv.reader(f, delimiter=',')
		first = True
		sku_dict = {}
		for sku_row in reader:
			if first:
				header = sku_row
				header_val_error, _ = self.validate_header(header)
				if header_val_error:
					errors.append(header_val_error)
					return errors, warnings
				first = False
				continue
			else:
				# {Ingr#: ingr, Name: ingr_name, etc.} for each ingredient 
				for idx, ele in enumerate(sku_row):
						sku_dict[header[idx]] = ele
				if not sku_dict['SKU#']:
					if not Sku.objects.all():
						default_id = 1
					else:
						default_id =  Sku.objects.all().order_by("-id")[0].id + 1
				else:
					try:
						int(sku_dict['SKU#'])
					except ValueError:
						errors.append(sku_dict['SKU#'] + " is not a number,")
						continue
					default_id = int(sku_dict['SKU#'])
				val_error, val_warning = self.validate_sku(sku_dict, default_id)
				if val_warning:
					warnings.append(val_warning)
				if val_error:
					errors.append(val_error)
					break
				product_line = Product_Line.objects.get(product_line_name=sku_dict['PL Name'])
				formula = Formula.objects.get(id=int(sku_dict['Formula#']))
				if not Sku.objects.filter(id=default_id).exists():
					serializer = SkuSerializer(data={'id':default_id,'productline':product_line.product_line_name,'caseupc':sku_dict['Case UPC'],'unitupc':sku_dict['Unit UPC'],'sku_name':sku_dict['Name'],'count':sku_dict['Count per case'],'unit_size':sku_dict['Unit size'],'formula':formula.id,'formula_scale_factor':sku_dict['Formula factor'],'manufacture_rate':sku_dict['Rate'],'comment':sku_dict['Comment']})
					if serializer.is_valid():
						serializer.save()
					else:
						errors.append(serializer.errors['caseupc'])
						break
				else:
					sku = Sku.objects.get(id=default_id)
					skutoml = Sku_To_Ml_Shortname.objects.filter(sku=default_id)
					for s in skutoml:
						s.delete()
					s = SkuSerializer(sku)
					s_data = s.data
					sku.delete()
					s_data['sku_name']=sku_dict['Name']
					s_data['productline']=product_line.product_line_name
					s_data['caseupc']=sku_dict['Case UPC']
					s_data['unitupc']=sku_dict['Unit UPC']
					s_data['count']=sku_dict['Count per case']
					s_data['unit_size']=sku_dict['Unit size']
					s_data['formula']=formula.id
					s_data['formula_scale_factor']=sku_dict['Formula factor']
					s_data['manufacture_rate']=sku_dict['Rate']
					s_data['comment']=sku_dict['Comment']
					serializer = SkuSerializer(data=s_data)
					# print(serializer)
					if(serializer.is_valid()):
						serializer.save()
					else:
						for error in serializer.errors.values():
							errors.append(error)
						break
				# save all manufacturing lines associated with sku
				ml_shortnames = sku_dict['ML Shortnames'].strip('"').split(',')
				for ml_shortname in ml_shortnames:
					if Sku_To_Ml_Shortname.objects.filter(sku=default_id,ml_short_name=ml_shortname).exists():
						continue
					sku_object = Sku.objects.get(id=default_id)
					ml_short_name_object = Manufacture_line.objects.get(ml_short_name=ml_shortname)
					sku2ml = ManufactureLineToSkuSerializer(data={'sku':sku_object.id,'ml_short_name':ml_short_name_object.ml_short_name})
					if(sku2ml.is_valid()):
						sku2ml.save()
						print(sku2ml.errors)

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
	def validate_sku(self, sku_dict, default_id):
		error = ''
		warning = ''
		case_upc = self.validate_case_upc(sku_dict)
		unit_upc = self.validate_unit_upc(sku_dict)
		print(sku_dict['Name'])
		# if ingredient with same name exists, only update if id matches
		if Sku.objects.filter(sku_name=sku_dict['Name']).exists():
			same_name_sku = Sku.objects.get(sku_name=sku_dict['Name'])
			if same_name_sku.pk != default_id:
				error = 'Ambiguous record for %s,' % same_name_sku.sku_name
			else:
				# update other fields
				warning = 'Update fields for %s,' % same_name_sku.sku_name
		elif not case_upc:
			error = 'Case UPC invalid for %s,' % sku_dict['Name']
		elif not unit_upc:
			 error = 'Unit UPC invalid for %s,' % sku_dict['Name']
		else:
			# check if object with same id exists
			if Sku.objects.filter(pk=default_id).exists():
				# overwrite existing object
				warning = 'Overwrite object with id %s' % str(default_id)
		# check if product line exists
		product_line_name = sku_dict['PL Name']
		if not Product_Line.objects.filter(product_line_name=product_line_name).exists():
			error = 'No product line named %s,' % product_line_name
		# check if formula exists
		formula = sku_dict['Formula#']
		if not Formula.objects.filter(id=formula).exists():
			print('bad formula')
			error = 'No Formula# %s,' % str(formula)
		# check if manufacturing lines exist 
		ml_shortnames = sku_dict['ML Shortnames'].strip('"').split(',')
		for ml_shortname in ml_shortnames:
			if not Manufacture_line.objects.filter(ml_short_name=ml_shortname).exists():
				error = 'No manufacturing line named %s,' % ml_shortname
				break
		print(sku_dict['Name'])
		return error, warning

	def validate_case_upc(self, sku_dict):
		if sku_dict['Case UPC'][0] == '2' or sku_dict['Case UPC'][0] == '3' or sku_dict['Case UPC'][0] == '4' or sku_dict['Case UPC'][0] == '5':
			return False
		odds = int(sku_dict['Case UPC'][0]) + int(sku_dict['Case UPC'][2]) + int(sku_dict['Case UPC'][4]) + int(sku_dict['Case UPC'][6]) + int(sku_dict['Case UPC'][8])+ int(sku_dict['Case UPC'][10])
		evens = int(sku_dict['Case UPC'][1]) + int(sku_dict['Case UPC'][3]) + int(sku_dict['Case UPC'][5]) + int(sku_dict['Case UPC'][7]) + int(sku_dict['Case UPC'][9])
		sumNum = odds*3 + evens
		print(sumNum)
		print(sku_dict['Case UPC'][11])
		if sumNum % 10 == 0 and int(sku_dict['Case UPC'][11]) != 0:
			return False
		elif sumNum % 10 != 0:
			check = 10 - (sumNum % 10)
			if int(sku_dict['Case UPC'][11]) != check:
				return False

		return True;

	def validate_unit_upc(self, sku_dict):
		if sku_dict['Unit UPC'][0] == '2' or sku_dict['Unit UPC'][0] == '3' or sku_dict['Unit UPC'][0] == '4' or sku_dict['Unit UPC'][0] == '5':
			return False
		odds = int(sku_dict['Unit UPC'][0]) + int(sku_dict['Unit UPC'][2]) + int(sku_dict['Unit UPC'][4]) + int(sku_dict['Unit UPC'][6]) + int(sku_dict['Unit UPC'][8])+ int(sku_dict['Unit UPC'][10])
		odds = odds*3
		evens = int(sku_dict['Unit UPC'][1]) + int(sku_dict['Unit UPC'][3]) + int(sku_dict['Unit UPC'][5]) + int(sku_dict['Unit UPC'][7]) + int(sku_dict['Unit UPC'][9])
		sumNum = odds + evens
		if sumNum % 10 == 0 and int(sku_dict['Unit UPC'][11]) != 0:
			return False
		elif sumNum % 10 != 0:
			check = 10 - (sumNum % 10)
			if int(sku_dict['Unit UPC'][11]) != check:
				return False
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
		try:
			csv_file = request.data['data']
			errors, warnings = self.save(csv_file)
			post_result = {'errors': errors, 'warnings': warnings}
			if errors != []:
				return Response(post_result, status.HTTP_400_BAD_REQUEST)
			return Response(post_result, status.HTTP_201_CREATED)
		except Exception as e: 
			return Response(status = status.HTTP_400_BAD_REQUEST)

		
	@transaction.atomic
	def save(self, formula_file):
		errors = []
		warnings = []
		# https://docs.djangoproject.com/en/1.9/topics/db/transactions/#savepoint-rollback
		transaction_savepoint = transaction.savepoint()
		f = io.StringIO(formula_file)
		reader = csv.reader(f, delimiter=',')
		firstA = True
		formula_dict = {}
		readers = list(reader)
		# print(readers)
		for formula_row in readers:
			if firstA:
				header = formula_row
				header_val_error, _ = self.validate_header(header)
				if header_val_error:
					errors.append(header_val_error)
					return errors, warnings
				firstA = False
				continue
			else:
				# {Ingr#: ingr, Name: ingr_name, etc.} for each ingredient 
				for idx, ele in enumerate(formula_row):
					formula_dict[header[idx]] = ele
					if not formula_dict['Formula#'] and not Formula.objects.filter(formula_name=formula_dict['Name']).exists():
						if not Formula.objects.all():
							default_id = 1
						else:
							default_id =  Formula.objects.all().order_by("-id")[0].id + 1
					elif formula_dict['Formula#']:
						try:
							int(formula_dict['Formula#'])
						except ValueError:
							errors.append(formula_dict['Formula#'] + " is not a number,")
							continue
						default_id = int(formula_dict['Formula#'])
					elif not formula_dict['Formula#'] and Formula.objects.filter(formula_name=formula_dict['Name']).exists():
						formula_exist = Formula.objects.get(formula_name=formula_dict['Name'])
						default_id = formula_exist.id
					if Formula.objects.filter(id=default_id).exists():
						formula1 = Formula.objects.get(id=default_id)
						ingrtoformula1 = Formula_To_Ingredients.objects.filter(formula=formula1.id)
						for entry in ingrtoformula1:
							entry.delete()
						formula1.delete()
		formula_dictA = {}
		first = True
		print('60')
		for formula_rowA in readers:
			if first:
				header = formula_rowA
				first = False
				continue
			else:
				for idx1, ele1 in enumerate(formula_rowA):
					print("*********")
					print(formula_rowA)
					print(header[idx1])
					formula_dictA[header[idx1]] = ele1
					# print(formula_dictA['Name'])
					print('61')
					if not formula_dictA['Formula#'] and not Formula.objects.filter(formula_name=formula_dictA['Name']).exists():
						if not Formula.objects.all():
							default_idA = 1
						else:
							default_idA =  Formula.objects.all().order_by("-id")[0].id + 1
					elif formula_dictA['Formula#']:
						print('61')
						try:
							int(formula_dictA['Formula#'])
							print("here")
						except ValueError:
							errors.append(formula_dictA['Formula#'] + " is not a number,")
							print("cont")
							continue
						default_idA = int(formula_dictA['Formula#'])
					elif not formula_dictA['Formula#'] and Formula.objects.filter(formula_name=formula_dictA['Name']).exists():
						formula_exist = Formula.objects.get(formula_name=formula_dictA['Name'])
						default_idA = formula_exist.id
				val_error, val_warning = self.validate_formula(formula_dictA, default_idA)
				unit_error = self.validate_unit(formula_dictA)
				# print('666')
				if val_warning:
					warnings.append(val_warning)
				if val_error:
					errors.append(val_error)
					print("break")
					break
				if not unit_error:
					errors.append("package size unit incorrect for %s" % formula_dictA['Name'])
					print('break')
					break
				# store formula first if not exist 
				print('666')
				if not Formula.objects.filter(id=default_idA).exists():
					# formula = Formula(formula_name=formula_dict['Name'],
					# 				  id=formula_dict['Formula#'],
					# 				  comment=formula_dict['Comment'])
					serializer = FormulaSerializer(data={'formula_name':formula_dictA['Name'],'id':default_idA,'comment':formula_dictA['Comment']})
					if(serializer.is_valid()):
						serializer.save()
					else:
						for error in serializer.errors.values():
							errors.append(error)
						break


				# add to Formula_To_Ingredients table if not exist
				formula = Formula.objects.get(id=default_idA)
				ingr = Ingredient.objects.get(id=formula_dictA['Ingr#'])
				if not Formula_To_Ingredients.objects.filter(formula=formula.id, ig=ingr.id).exists():
					serializer = IngredientToFormulaSerializer(data={'formula':default_idA,'ig':ingr.id,'quantity':formula_dictA['Quantity']})
					# save without commit, as later validation might fail 
					# print(serializer.is_valid())
					# print(serializer.data)
					if(serializer.is_valid()):
						serializer.save()
					else:
						for error in serializer.errors.values():
							errors.append(error)
						break
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
	def validate_formula(self, formula_dictA,default_idA):
		error = ''
		warning = ''
		print('66')
		print('77')
		print(formula_dictA['Ingr#'])
		if not Ingredient.objects.filter(id=formula_dictA['Ingr#']).exists():
			error = 'No ingredient with id %s,' % formula_dictA['Ingr#']
		print('99')
		# check if formula exist
		# if formula name exists but a different id, error
		if Formula.objects.filter(formula_name=formula_dictA['Name']).exists():
			same_name_formula = Formula.objects.get(formula_name=formula_dictA['Name'])
			if same_name_formula.pk != default_idA:
				error = 'Ambiguous record for %s,' % same_name_formula.formula_name
			else:
				# update other fields
				if same_name_formula.formula_name != formula_dictA['Name']:
					warning = 'Update fields for %s,' % same_name_formula.formula_name
		# if formula id exists but a different name, replace
		elif Formula.objects.filter(pk=default_idA).exists():
				# overwrite existing object
				warning = 'Overwrite object with id %s,' % str(default_idA)
		print('88')
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
		response['Content-Disposition'] = "attachment; filename=\"formulas.csv\""
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
		try:
			csv_file = request.data['data']
			# print(csv_file)
			directory = os.getcwd()
			# response = HttpResponse(content_type='text/csv')
			# response['Content-Disposition'] = "attachment; filename=\"product_line.csv\""f
			csv_file = csv_file.split('\n')
			headers =csv_file[0].split(',')
			writer = csv.writer(open(directory+"/outputpl.csv", 'w'))
			writer.writerow(headers)
			for i in range(1, len(csv_file)):
				row = csv_file[i].split(',')
				writer.writerow(row)
				# b = bytes(line, 'utf-8')
			# print(response)
			errors, warnings = self.save(csv_file)
			post_result = {'errors': errors, 'warnings': warnings}
			if errors != []:
				return Response(post_result, status.HTTP_400_BAD_REQUEST)
			return Response(post_result, status.HTTP_201_CREATED)
		except Exception as e: 
			return Response(status = status.HTTP_400_BAD_REQUEST)

	@transaction.atomic
	def save(self, product_line_file):
		errors = []
		warnings = []
		# https://docs.djangoproject.com/en/1.9/topics/db/transactions/#savepoint-rollback
		transaction_savepoint = transaction.savepoint()
		directory = os.getcwd()
		with open(directory+"/outputpl.csv") as f:
			reader = csv.DictReader(product_line_file)
			print(reader.fieldnames)
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
			error = 'Existing product line: %s,' % product_line_dict['Name']
		return error, warning