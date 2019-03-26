from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
import uuid
from datetime import date
from jsonfield import JSONField	

# product_line to sku is one to many. Each sku matches to exactly one product line
class Product_Line(models.Model):
	product_line_name = models.CharField(max_length=128, primary_key=True, unique=True, null=False, editable = True)

class Formula(models.Model):
	formula_name = models.CharField(max_length=32, unique=True, null=False, default='')
	id = models.BigIntegerField(primary_key=True)
	comment = models.TextField(null=True, blank = True)

	def save(self, *args, **kwargs):
		if self.id == 0:
			if not self.__class__.objects.all():
				self.id = 1
			else:
				self.id =  self.__class__.objects.all().order_by("-id")[0].id + 1
		super(self.__class__, self).save(*args, **kwargs)

class Sku(models.Model):
	id = models.BigIntegerField(unique = True, primary_key=True)
	caseupc = models.CharField(null=False, default=100000000000,unique=True, 
		max_length=12, validators=[RegexValidator(r'^\d{12,12}$', message="UPC not 12 digits", code = "invalid UPC")])
	unitupc = models.CharField(null=False, default=100000000000,
		max_length=12, validators=[RegexValidator(r'^\d{12,12}$', message="UPC not 12 digits", code = "invalid UPC")])
	sku_name = models.CharField(max_length=32, null=False, default='')
	count = models.PositiveIntegerField(null=False, default=0) 
	unit_size = models.CharField(max_length=128, null=False, default='')
	comment = models.TextField(null=True, blank = True)
	productline = models.ForeignKey(Product_Line, on_delete=models.CASCADE, default='')
	formula = models.ForeignKey(Formula, on_delete=models.CASCADE, default = 1)
	formula_scale_factor = models.FloatField(null=False, default=1.0)
	manufacture_rate = models.FloatField(null=False, default=1.0)
	manufacture_setup_cost = models.DecimalField(null=False, decimal_places=2, max_digits=32, default=1.0)
	manufacture_run_cost = models.DecimalField(null=False, decimal_places=2, max_digits=32, default=1.0)

	def save(self, *args, **kwargs):
		if self.id == 0:
			if not self.__class__.objects.all():
				self.id = 1
			else:
				self.id =  self.__class__.objects.all().order_by("-id")[0].id + 1
		super(self.__class__, self).save(*args, **kwargs)

class Ingredient(models.Model):
	id = models.BigIntegerField(primary_key=True)
	ingredient_name = models.CharField(max_length=128, unique=True, null=False, default='')
	description = models.TextField(null=True, blank = True) 
	package_size = models.CharField(max_length=128,null=False, default = '',
		validators=[RegexValidator(r'^(\d*\.?\d+)\s*(\D.*|)$', message="package size not up to standard", code = "invalid package size")])
	cpp = models.FloatField(null=True)
	comment = models.TextField(null=True, blank = True)

	# def __unicode__(self):
 #        return u'%s %s' % (self.first_name, self.last_name)

	def save(self, *args, **kwargs):
		if self.id == 0:
			if not self.__class__.objects.all():
				self.id = 1
			else:
				self.id =  self.__class__.objects.all().order_by("-id")[0].id + 1
		super(self.__class__, self).save(*args, **kwargs)

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
	id = models.BigIntegerField(primary_key=True, null = False)
	name = models.CharField(max_length=128, unique = True)

class Sku_To_Customer(models.Model):
	id = models.BigIntegerField(primary_key=True, null=False)
	sku = models.ForeignKey(Sku,on_delete=models.CASCADE)
	customer = models.ForeignKey(Customer,on_delete=models.CASCADE)

	class Meta:
		unique_together = (("sku","customer"),)

class Sale_Record(models.Model):
	sku = models.ForeignKey(Sku,on_delete=models.CASCADE)
	sale_date = models.DateField(default=date.today, null=False, editable=True)
	customer_id = models.ForeignKey(Customer,on_delete=models.CASCADE)
	customer_name = models.CharField(max_length=128,unique=True,null=False,default='')
	sales = models.PositiveIntegerField()
	price_per_case = models.DecimalField(null=False,max_digits=12, decimal_places=2, default=1.0)

class Manufacture_Goal(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	sku = models.ForeignKey(Sku,on_delete=models.CASCADE)
	name = models.ForeignKey(Goal,on_delete=models.CASCADE)
	goal_sku_name = models.CharField(max_length=128, null=False, default='')
	desired_quantity = models.PositiveIntegerField()


	class Meta: 
		unique_together = (("name","sku"),)

class Manufacture_line(models.Model):
	ml_name = models.CharField(max_length=32, null=False, default='')
	ml_short_name = models.CharField(primary_key = True, max_length=5, null=False, unique=True, editable = True,
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

class Scheduler(models.Model):
	items = models.TextField(null=False,default='')
	groups = models.TextField(null=False,default='')
	scheduled_goals = models.TextField(null=False,default='')
	unscheduled_goals = models.TextField(null=False,default='')
	manufacturing_lines = models.TextField(null=False,default='')
		
# Keep track of sku status on manufacture lines 
class Manufacture_Line_Skus(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	manufacture_line_short_name = models.ForeignKey(Manufacture_line,on_delete=models.CASCADE)
	sku_id = models.ForeignKey(Sku,on_delete=models.CASCADE)
	goal_name = models.ForeignKey(Goal, on_delete=models.CASCADE, to_field='goalname')
	start = models.DateTimeField(auto_now_add=False)
	end = models.DateTimeField(auto_now_add=False)
	duration = models.PositiveIntegerField(null=False, default=0) 
	# # active if the associated manufacture goal is being scheduled 
	# STATUS_CHOICES = ['active', 'orphaned']
	# status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

	class Meta:
		unique_together = (("user","sku_id", 'goal_name'),)
