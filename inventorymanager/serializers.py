from rest_framework import serializers
from .models import *


# Serializer serializes model data
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class SkuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sku
        fields = '__all__'

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'

# For uploaded Ingredient File 
class IngredientFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientFile
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class ManufactureGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacture_Goal
        fields = '__all__'

# models not having a serializers yet 
# class sku_to_ingredients(models.Model):
# 	sku = models.ForeignKey(sku,on_delete=models.CASCADE,primary_key=True)
# 	ig = models.ForeignKey(ingredients,on_delete=models.CASCADE)

# 	class Meta:
# 		unique_together = (("sku","ig"),)

# class sku_to_customer(models.Model):
# 	sku = models.ForeignKey(sku,primary_key=True,on_delete=models.CASCADE)
# 	customer = models.ForeignKey(customer,on_delete=models.CASCADE)

# 	class Meta:
# 		unique_together = (("sku","customer"),)
