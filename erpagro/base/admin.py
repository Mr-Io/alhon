from django.contrib import admin

from .models import Contact

class ContactInline(admin.TabularInline):
    model = Contact
    fk_name = "agent"
    fields = ["name", "mobile", "email"]
    extra = 0


class AgentAdmin(admin.ModelAdmin):

    fieldsets = [("Datos comerciales", {"fields": [("name", "cif"), ("email"), ("address"), ("phone", "mobile", "fax")]})]
    list_display = ["name", "cif"]
    search_fields = list_display

    inlines = [ContactInline]


