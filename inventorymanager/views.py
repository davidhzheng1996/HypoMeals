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
	return render(request, 'ingredient.html')

@login_required(login_url='/accounts/login/')
def sku(request):
	return render(request, "sku.html")

# https://blog.vivekshukla.xyz/uploading-file-using-api-django-rest-framework/
# https://www.django-rest-framework.org/api-guide/views/
# APIView is specific for handling REST API requests. User need to Explicitly describe  
# the logic for post, get, delete, etc. If not described, action is not allowed. 
# We do not use ViewSet for IngredientFile because user should not be able issue GET or
# DELETE requests for IngredientFile 
class IngredientFileView(APIView):
	# available parsers: https://www.django-rest-framework.org/api-guide/parsers/ 
	# file sent should be in FormData
	parser_classes = (MultiPartParser, FormParser)
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

	
@login_required(login_url='/accounts/login/')
def manufacture_goal(request):
	return render(request, "manufacturing.html")
