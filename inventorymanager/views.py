from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required(login_url='/accounts/login/')
def index(request):
	return HttpResponse("Hello. You are at starting point index.")

@login_required(login_url='/accounts/login/')
def ingredient(request):
	return render(request, 'ingredient.html')

@login_required(login_url='/accounts/login/')
def sku(request):
	return render(request, "sku.html")