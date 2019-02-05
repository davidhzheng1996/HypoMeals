from django.db import models
from django.contrib.auth.models import User

# product_line to sku is one to many. Each sku matches to exactly one product line
class Product_Line(models.Model):
	product_line_name = models.CharField(max_length=128, unique=True, null=False, default='')

class Sku(models.Model):
	caseupc = models.FloatField(null=False, default=1000)
	unitupc = models.FloatField(null=True, default=1000)
	sku_name = models.CharField(max_length=128, unique=True, null=False, default='')
	count = models.IntegerField(null=True)
	unit_size = models.CharField(max_length=128, null=True)
	tuples = models.TextField(null=True)
	comment = models.TextField(null=True)
	productline = models.ForeignKey(Product_Line,on_delete=models.CASCADE)

class Ingredient(models.Model):
	ingredient_name = models.CharField(max_length=128, unique=True, null=False, default='')
	description = models.TextField(null=True) 
	package_size = models.CharField(max_length=128,null=True)
	cpp = models.IntegerField(null=True)
	comment = models.TextField(null=True)

class Goal(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	goalname = models.CharField(max_length=128,null=False,default='')


class IngredientFile(models.Model):
	file = models.FileField(blank=False, null=False)
	description = models.TextField(null=True) 
	timestamp = models.DateTimeField(auto_now_add=True)

class SkuFile(models.Model):
	file = models.FileField(blank=False, null=False)
	description = models.TextField(null=True) 
	timestamp = models.DateTimeField(auto_now_add=True)


class Sku_To_Ingredient(models.Model):
	sku = models.ForeignKey(Sku,on_delete=models.CASCADE)
	ig = models.ForeignKey(Ingredient,on_delete=models.CASCADE)
	quantity = models.IntegerField(null=False,default=1)

	class Meta:
		unique_together = (("sku","ig"),)

class Customer(models.Model):
	name = models.CharField(max_length=128)

class Sku_To_Customer(models.Model):
	id = models.BigIntegerField(primary_key=True, null=False)
	sku = models.ForeignKey(Sku,on_delete=models.CASCADE)
	customer = models.ForeignKey(Customer,on_delete=models.CASCADE)

	class Meta:
		unique_together = (("sku","customer"),)

class Manufacture_Goal(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	sku = models.ForeignKey(Sku,on_delete=models.CASCADE)
	name = models.ForeignKey(Goal,on_delete=models.CASCADE)
	goal_sku_name = models.CharField(max_length=128, null=False, default='')
	desired_quantity = models.IntegerField()

	class Meta: 
		unique_together = (("user","sku"),)



