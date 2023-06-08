from django.contrib import admin
from django.http.request import HttpRequest

from .models import Supplier, SupplierGroup, Entry, EntryNote, Invoice, CarrierAgent, Charge
from packaging.models import Transaction
from base.admin import AgentAdmin 
# Register your models here.


########### CARRIER AGENT ############
class CarrierAgentAdmin(AgentAdmin):
    fieldsets = AgentAdmin.fieldsets + [("Costes", {"fields": [("carrier_price")]})]

########### SUPPLIER ############
class SupplierAdmin(AgentAdmin):
    fieldsets = AgentAdmin.fieldsets + [("Agrupación", {"fields": [("group", "share")]}),
                                        ("Gastos", {"fields": [("charge"), ("carrier", "carrier_price")]}),
                                        ]
                                       
    list_display = AgentAdmin.list_display + ["group", "share", "carrier"]

########### SUPPLIER GROUP ############
class SupplierInline(admin.TabularInline):
    fields = ["name", "share"]
    model = Supplier
    extra = 0

    def has_add_permission(*args) -> bool:
        return False

class SuplierGroupAdmin(admin.ModelAdmin):
    fields = ["name"]
    list_display = ["name"]
    search_fields = ["name"]

    inlines = [SupplierInline]

########### ENTRY ############

class EntryAdmin(admin.ModelAdmin):
    fields = [("warehouse"), ("agrofood", "weight"), ("packaging_transaction"),("entry_note",), ("price",)] 
    date_hierarchy = "entry_note__creation_date"
    list_display = ["entry_note", "agrofood", "weight", "price", "total_price"]
    search_fields = ["agrofood", "entry_note__supplier", "weight"]

########### ENTRY NOTE ############

class EntryInline(admin.TabularInline):
    fields = EntryAdmin.fields
    model = Entry
    extra = 0

class EntryNoteAdmin(admin.ModelAdmin):
    fields = [("supplier", "charge"), ("carrier", "carrier_price"), ("invoice") ]
    date_hierarchy = "creation_date"
    list_display = ["pk", "creation_date", "supplier", "invoice"]
    search_fields = ["supplier"]
    list_filter = ["creation_date"]

    inlines = [EntryInline]

########### INVOICE ############
class EntryNoteInline(admin.TabularInline):
    model = EntryNote
    extra = 0
    fields = EntryNoteAdmin.fields

class InvoiceAdmin(admin.ModelAdmin):
    fields = ["settled", "paid"]
    date_hierarchy = "creation_date"
    list_display = ["pk", "creation_date", "settled", "paid"]
    list_filter = ["creation_date", "settled", "paid"]

    inlines = [EntryNoteInline]

    def has_add_permission(*args) -> bool:
        return False

    def has_change_permission(*args) -> bool:
        return False


########### INVOICE ############
class ChargeAdmin(admin.ModelAdmin):
    fieldsets = [("datos",{"fields": [("name")]}), ("gastos", {"fields": ["comision", "descarga", "analisis", "portes", "embalajes"]})]



admin.site.register(Supplier, SupplierAdmin)
admin.site.register(SupplierGroup, SuplierGroupAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(EntryNote, EntryNoteAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(CarrierAgent, CarrierAgentAdmin)
admin.site.register(Charge, ChargeAdmin)
