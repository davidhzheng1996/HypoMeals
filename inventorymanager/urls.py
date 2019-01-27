from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ingredient',views.ingredient),
    path('sku',views.sku),
    path('manufacture_goal', views.manufacture_goal)
]