from django.contrib import admin

from .models import Supplier, SupplierGroup, Entry, EntryNote, Invoice, CarrierAgent, Charge
from base.admin import AgentAdmin 
from quality.admin import LandInline
from sales.models import Exit

########### CARRIERAGENT ############
class CarrierAgentAdmin(AgentAdmin):
    fieldsets = AgentAdmin.fieldsets + [("Costes", {"fields": [("carrier_price")]})]

########### SUPPLIER ############
class SupplierAdmin(AgentAdmin):
    fieldsets = AgentAdmin.fieldsets + [("Agrupación", {"fields": [("group", "share")]}),
                                        ("Gastos", {"fields": [("charge"), ("carrier")]}),
                                        ]
                                       
    list_display = AgentAdmin.list_display + ["group", "share", "carrier"]

    inlines = AgentAdmin.inlines + [LandInline]

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
class ExitInline(admin.TabularInline):
    model = Exit
    extra = 0

class EntryAdmin(admin.ModelAdmin):
    fields = [("warehouse"), ("agrofood", "weight"), ("packaging_transaction"),("entrynote",), ("price",)] 
    date_hierarchy = "entrynote__creation_date"
    list_display = ["pk","entrynote", "agrofood", "weight", "in_warehouse", "pending", "price", "total_price"]
    search_fields = ["agrofood", "entrynote__supplier", "weight"]
    list_filter = ["agrofood"]

    inlines = [ExitInline]

########### ENTRY NOTE ############

class EntryInline(admin.TabularInline):
    fields = EntryAdmin.fields
    model = Entry
    extra = 0

class EntryNoteAdmin(admin.ModelAdmin):
    fields = [("supplier", "charge"), ("carrier", "carrier_price"), ("registered"), ("invoice") ]
    date_hierarchy = "creation_date"
    list_display = ["pk", "creation_date", "supplier", "invoice", "priced", "registered"]
    search_fields = ["supplier"]
    list_filter = ["registered", "creation_date"]

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
