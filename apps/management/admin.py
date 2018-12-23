# Register your models here.
from django.contrib.auth import get_user_model
from django.contrib import admin
from .models import Charge

User = get_user_model()


class ChargetAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "bill_manager":
            kwargs["queryset"] = User.objects.filter(is_bill=True)  # 只显示票据管理员
        return super(ChargetAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    list_display = ('id', 'account_number', 'account_name', 'bill_manager')
    search_fields = ('account_name', 'account_number', 'bill_manager__name')
    list_filter = ('account_name', 'account_number', 'bill_manager')


admin.site.register(Charge, ChargetAdmin)

admin.site.site_header = '电费账务管理系统后台'
admin.site.site_title = '电费账务管理系统后台'
