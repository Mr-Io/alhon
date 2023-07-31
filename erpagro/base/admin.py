from django.contrib import admin

from .models import Contact

class ContactInline(admin.TabularInline):
    model = Contact
    fk_name = "agent"
    fields = ["name", "mobile", "email"]
    extra = 0


class AgentAdmin(admin.ModelAdmin):

    fieldsets = [("Datos comerciales", {"fields": [("name", "cif"), ("email"), ("phone", "mobile", "fax")]}),
                 ("Dirección Fiscal", {"fields": ["country", ("postal_code", "state"), ("city", "address_line"),]})]
    list_display = ["pk", "name", "cif"]
    search_fields = ["name", "cif"]

    inlines = [ContactInline]

class AddressAbstractAdmin(admin.ModelAdmin):
    fieldsets = [("Dirección", {"fields": ["country", ("postal_code", "state"), ("city", "address_line"),]})]


