from django.db import models

# Create your models here.
class users(models.Model):
	# The PRIMARY KEY ID IS AUTO GENERATED FOR ALL MODELS 
	username = models.CharField(max_length=64)
	password = models.CharField(max_length=128)

class sku(models.Model):
	productline = models.CharField(max_length=256)
	caseupc = models.IntegerField(null=True)
	unitupc = models.IntegerField(null=True)

class ingredients(models.Model):
	name = models.CharField(max_length=128)
	description = models.TextField(null=True) 
	package_size = models.CharField(max_length=128,null=True)
	cpp = models.IntegerField(null=True)

class sku_to_ingredients(models.Model):
	sku_id = models.ForeignKey(sku,on_delete=models.CASCADE,primary_key=True)
	ig_id = models.ForeignKey(ingredients,on_delete=models.CASCADE)

	class Meta:
		unique_together = (("sku_id","ig_id"),)

class customer(models.Model):
	name = models.CharField(max_length=128)

class sku_to_customer(models.Model):
	sku_id = models.ForeignKey(sku,primary_key=True,on_delete=models.CASCADE)
	customer_id = models.ForeignKey(customer,on_delete=models.CASCADE)

	class Meta:
		unique_together = (("sku_id","customer_id"),)

class manufacturing_goals(models.Model):
	user_id = models.ForeignKey(users,primary_key=True,on_delete=models.CASCADE)
	sku_id = models.ForeignKey(sku,on_delete=models.CASCADE)
	desired_quantity = models.IntegerField()

	class Meta: 
		unique_together = (("user_id","sku_id"),)