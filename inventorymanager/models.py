from django.db import models
from django.contrib.auth.models import User

# product_line to sku is one to many. Each sku matches to exactly one product line
class Product_Line(models.Model):
	product_line_name = models.CharField(max_length=128, unique=True, null=False, default='')

class Sku(models.Model):
	id = models.IntegerField(primary_key=True, null=False, unique=True)
	caseupc = models.FloatField(null=False, default=0)
	unitupc = models.FloatField(null=True, default=0)
	sku_name = models.CharField(max_length=32, null=False, default='')
	count = models.IntegerField(null=True)
	unit_size = models.CharField(max_length=128, null=True)
	comment = models.TextField(null=True)
	productline = models.ForeignKey(Product_Line,on_delete=models.CASCADE)

class Ingredient(models.Model):
	id = models.IntegerField(primary_key=True, null=False, unique=True)
	ingredient_name = models.CharField(max_length=128, unique=True, null=False, default='')
	description = models.TextField(null=True) 
	package_size = models.CharField(max_length=128,null=True)
	cpp = models.FloatField(null=True)
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
	quantity = models.DecimalField(null=False,max_digits=7, decimal_places=3, default=1.0)

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
		unique_together = (("name","sku"),)

class Formula(models.Model):
	formula_name = models.CharField(max_length=32, null=False, default='')
	id = models.IntegerField(primary_key=True, null=False, unique=True)
	comment = models.TextField(null=True)

class Manufacture_line(models.Model):
	ml_name = models.CharField(max_length=32, null=False, default='')
	ml_short_name = models.CharField(primary_key = True, max_length=5, null=False, unique=True)
	comment = models.TextField(null=True)

# class sku_to_ml(models.Model):
# 	sku = models.ForeignKey(Sku,on_delete=models.CASCADE)
# 	ml_short_name = models.ForeignKey(Manufacture_line, on_delete=models.CASCADE)

# class Formula_Ingredients(models.Model):
# 	formula = models.ForeignKey(Formula, on_delete=models.CASCADE)
# 	ig = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
# 	quantity = models.DecimalField(null=False,max_digits=7, decimal_places=3, default=1.0)

		

