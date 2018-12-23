# Register your models here.

from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import UserProfile


class UserAdmins(UserAdmin, admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'username', 'name', 'password', 'is_superuser', 'is_active', 'birthday', 'gender', 'mobile', 'email',
                'is_bill', 'is_charge', 'is_check_charge', 'is_check_arrears', 'is_staff', 'add_time')
        }),)

    list_display = ('username', 'name', 'is_bill', 'is_charge', 'is_check_charge', 'is_check_arrears')
    search_fields = ('username', 'name', 'is_bill', 'is_charge', 'is_check_charge', 'is_check_arrears')


admin.site.register(UserProfile, UserAdmins)
