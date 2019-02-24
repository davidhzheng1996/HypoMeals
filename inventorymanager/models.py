from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
import uuid
from datetime import date

# product_line to sku is one to many. Each sku matches to exactly one product line
class Product_Line(models.Model):
	product_line_name = models.CharField(max_length=128, primary_key=True, unique=True, null=False)

class Formula(models.Model):
	formula_name = models.CharField(max_length=32, unique=True, null=False, default='')
	id = models.BigIntegerField(primary_key=True, null=False, unique=True)
	comment = models.TextField(null=True)

class Sku(models.Model):
	id = models.BigIntegerField(primary_key=True, unique=True, null=False)
	caseupc = models.CharField(null=False, default=100000000000,unique=True, 
		max_length=12, validators=[RegexValidator(r'^\d{12,12}$', message="UPC not 12 digits", code = "invalid UPC")])
	unitupc = models.CharField(null=False, default=100000000000,unique=False,
		max_length=12, validators=[RegexValidator(r'^\d{12,12}$', message="UPC not 12 digits", code = "invalid UPC")])
	sku_name = models.CharField(max_length=32, null=False, default='')
	count = models.PositiveIntegerField(null=False, default=0) 
	unit_size = models.CharField(max_length=128, null=False, default='')
	comment = models.TextField(null=True)
	productline = models.ForeignKey(Product_Line, on_delete=models.CASCADE, default='')
	formula = models.ForeignKey(Formula, on_delete=models.CASCADE, default = 1)
	formula_scale_factor = models.FloatField(null=False, default=1.0)
	manufacture_rate = models.FloatField(null=False, default=1.0)

	# def clean_caseupc(self):
	# 	caseupc = self.cleaned_data['caseupc']
	# 	if caseupc[0] == '2' or caseupc[0] == '3' or caseupc[0] == '4' or caseupc[0] == '5':
	# 		raise ValidationError('Leading number incorrect', code = 'invalid leading num')
	# 	else:
	# 		return caseupc

class Ingredient(models.Model):
	id = models.BigIntegerField(primary_key=True, unique=True, null=False)
	ingredient_name = models.CharField(max_length=128, unique=True, null=False, default='')
	description = models.TextField(null=True) 
	package_size = models.CharField(max_length=128,null=False, default = '',
		validators=[RegexValidator(r'^(\d*\.?\d+)\s*(\D.*|)$', message="Package size not up to standard", code = "invalid package_size")])
	cpp = models.FloatField(null=False, default=1.0)
	comment = models.TextField(null=True)

class Goal(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	goalname = models.CharField(max_length=128,unique=True,null=False,default='')
	deadline = models.DateField(default=date.today, null=False, editable=True)


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

class Manufacture_line(models.Model):
	ml_name = models.CharField(max_length=32, null=False, default='')
	ml_short_name = models.CharField(primary_key = True, max_length=5, null=False, unique=True,
		validators=[RegexValidator(r'^[a-zA-Z0-9\S]{1,5}$', message="Short name can have only Alphabets and Numbers", code = "invalid Short name")])
	comment = models.TextField(null=True)

class Sku_To_Ml_Shortname(models.Model):
	sku = models.ForeignKey(Sku,on_delete=models.CASCADE)
	ml_short_name = models.ForeignKey(Manufacture_line, on_delete=models.CASCADE)

	class Meta:
		unique_together = (("sku","ml_short_name"),)

class Formula_To_Ingredients(models.Model):
	formula = models.ForeignKey(Formula, on_delete=models.CASCADE)
	ig = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
	quantity = models.CharField(max_length=128,null=False, default = '',
		validators=[RegexValidator(r'^(\d*\.?\d+)\s*(\D.*|)$', message="quantity size not up to standard", code = "invalid quantity size")])

	class Meta:
		unique_together = (("formula","ig"),)

		

