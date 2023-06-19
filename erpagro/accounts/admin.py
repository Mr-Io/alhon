from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User
# Register your models here.

class UserAdminCustom(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('Agricultor', {"fields": [("supplier")]}),)
    list_display = ('username', "supplier", 'is_active')
    list_filter = ('is_staff', 'is_superuser')
    search_fields = ('username',)

admin.site.register(User, UserAdminCustom)