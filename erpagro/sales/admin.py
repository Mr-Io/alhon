from typing import Optional
from django.contrib import admin
from django.http.request import HttpRequest

from base.admin import AgentAdmin
from .models import Exit, Invoice, Client, CommissionAgent
# Register your models here.

gastos_fieldsets = [("Gastos",{"fields": [("commission", "commission_agent"), ("rapell"), ("porte"), ("fianza"), ("charge")]})]
 
########### CARRIER AGENT ############
class CommissionAgentAdmin(AgentAdmin):
    fieldsets = AgentAdmin.fieldsets + [("Costes", {"fields": [("commission")]})]

########### CLIENT ############
class ClientAdmin(AgentAdmin):
    fieldsets = AgentAdmin.fieldsets + gastos_fieldsets

########### SALE ############
class ExitAdmin(admin.ModelAdmin):
    fieldsets = [("Datos", {"fields":[("client"), ("entry", "weight"), ("packaging_transaction"),("price"), ("invoice"), ("in_warehouse")]})]
    date_hierarchy = "creation_date"
    list_display = ["pk", "creation_date", "client", "entry", "weight", "price", "invoice", "in_warehouse"] 
    search_fields = ["pk", "client"]
    list_filter = ["creation_date", "entry__agrofood__subfamily__family"]


########### INVOICE ############
class ExitInline(admin.TabularInline):
    model = Exit 
    extra = 0
    fields = ExitAdmin.fields

    def has_add_permission(*__) -> bool:
        return False

    def has_change_permission(*__)-> bool:
        return False

    def has_delete_permission(*__)-> bool:
        return False

class InvoiceAdmin(admin.ModelAdmin):
    fieldsets = [("Datos",{"fields": [("settled", "paid")]})] + gastos_fieldsets
    date_hierarchy = "creation_date"
    list_display = ["pk", "creation_date", "settled", "paid"]
    list_filter = ["creation_date", "settled", "paid"]
    readonly_fields = ["commission", "commission_agent", "rapell", "porte", "fianza", "charge"]

    inlines = [ExitInline]

    def has_add_permission(*__) -> bool:
        return False

    def has_change_permission(*__)-> bool:
        return False

    def has_delete_permission(*__)-> bool:
        return False


admin.site.register(Client, ClientAdmin)
admin.site.register(Exit, ExitAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(CommissionAgent, CommissionAgentAdmin)