from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('username','is_analyst','is_product_manager','is_business_manager','is_plant_manager','is_superuser')
    list_filter = ('username', 'is_analyst','is_product_manager','is_business_manager','is_plant_manager','is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {'fields': ('is_analyst','is_product_manager','is_business_manager','is_plant_manager','is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_analyst','is_product_manager','is_business_manager','is_plant_manager','is_superuser')}
        ),
    )
    search_fields = ('username',)
    ordering = ('username',)


admin.site.register(User, CustomUserAdmin)