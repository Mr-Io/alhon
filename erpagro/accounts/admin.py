from typing import Optional
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http.request import HttpRequest

from base.admin import AgentAdmin

from .models import User, Company
# Register your models here.

class UserAdminCustom(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('Agente', {"fields": [("agent")]}),)
    list_display = ('username', "agent", "is_staff", "is_superuser", 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username',)


class CompanyAdmin(admin.ModelAdmin):
    fieldsets = AgentAdmin.fieldsets + [("dirección", {"fields": [("address_line2")]}),
                                        ("facturación", {"fields": [("tax_start"), ("invoice_line")]}),
                                        ("correos", {"fields": [("post_box")]}),]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
    
    def has_delete_permission(self, request: HttpRequest, *args, **kwargs) -> bool:
        return False

admin.site.register(User, UserAdminCustom)
admin.site.register(Company, CompanyAdmin)