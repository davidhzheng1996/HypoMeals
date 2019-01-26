from django.db import models

# Create your models here.
class User(models.Model):
	# The PRIMARY KEY ID IS AUTO GENERATED FOR ALL MODELS 
	username = models.CharField(max_length=64)
	password = models.CharField(max_length=128)

class Sku(models.Model):
	productline = models.CharField(max_length=256)
	caseupc = models.IntegerField(null=False, default=1000)
	unitupc = models.IntegerField(null=True, default=1000)
	sku_name = models.CharField(max_length=128, null=False, default='')
	count = models.IntegerField(null=True)
	unit_size = models.CharField(max_length=128, null=True)
	tuples = models.TextField(null=True)
	comment = models.TextField(null=True)

class Ingredient(models.Model):
	ingredient_name = models.CharField(max_length=128, null=False, default='')
	description = models.TextField(null=True) 
	package_size = models.CharField(max_length=128,null=True)
	cpp = models.IntegerField(null=True)
	comment = models.TextField(null=True)

class Sku_To_Ingredient(models.Model):
	sku = models.ForeignKey(Sku,on_delete=models.CASCADE)
	ig = models.ForeignKey(Ingredient,on_delete=models.CASCADE)

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
	desired_quantity = models.IntegerField()

	class Meta: 
		unique_together = (("user","sku"),)