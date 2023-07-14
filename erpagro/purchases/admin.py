from typing import Any, List, Optional, Tuple, Union
from django.contrib import admin
from django.http.request import HttpRequest

from .models import Supplier, Entry, EntryNote, Settlement, Invoice, CarrierAgent, Charge
from base.admin import AgentAdmin
from archive.admin import PdfFieldAbstractAdmin, PdfFieldAbstractInline
from quality.admin import LandInline
from sales.models import Exit

########### CARRIERAGENT ############
class CarrierAgentAdmin(AgentAdmin):
    fieldsets = AgentAdmin.fieldsets + [("Costes", {"fields": [("carrier_price")]})]
    list_display = ["name", "carrier_price"]
    search_fields = ["name"]


########### SUPPLIER ############
class SupplierAdmin(AgentAdmin):
    fieldsets = AgentAdmin.fieldsets + [("Gastos", {"fields": [("charge"), ("carrier")]}),
                                        ("Facturación", {"fields": [("regime")]}),
                                        ("Agrupación", {"fields": [("group")]}),
                                        ]
                                       
    list_display = AgentAdmin.list_display + ["charge", "serial", "regime", "group", "carrier", "user"]
    list_filter = ["charge",  "regime", "regime__serial"]
    search_fields = ("name", "serial")
    list_display_links = ["name", "charge", "regime", "group", "carrier", "user"]
    def serial(self, obj):
        return obj.regime.serial
    serial.admin_order_field = "supplier"
    serial.short_description = "serie"

    inlines = AgentAdmin.inlines + [LandInline]

########### SUPPLIER GROUP ############
class SupplierInline(admin.TabularInline):
    fields = ["name"]
    model = Supplier
    extra = 0

    def has_change_permission(*args, **kwargs) -> bool:
        return False

    def has_delete_permission(*args, **kwargs) -> bool:
        return False

    def has_add_permission(*args, **kwargs) -> bool:
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
    list_display = ["pk","entrynote", "warehouse", "agrofood", "packaging_transaction", "weight", "pending", "sent", "price", "base_amount", "creation_date"]
    search_fields = ["agrofood", "entrynote__supplier"]
    list_filter = ["agrofood"]

    inlines = [ExitInline]


    def get_readonly_fields(self, request: HttpRequest, obj: Any | None = ...) -> List[str] | Tuple[Any, ...]:
        if obj and obj.entrynote.invoice:
            return ["warehouse", "agrofood", "weight", "packaging_transaction", "entrynote", "price"]
        return super().get_readonly_fields(request, obj)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
    
    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        if obj and obj.entrynote.invoice:
            return False
        return super().has_delete_permission(request, obj)

########### ENTRY NOTE ############

class EntryInline(admin.TabularInline):
    fields = EntryAdmin.fields
    model = Entry
    extra = 0
    min_num = 1

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        if obj and obj.invoice:
            return False
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request: HttpRequest, obj: Any | None = ...) -> bool:
        if obj and (obj.invoice or  obj.entry_set.count() <= 1):
            return False
        return super().has_delete_permission(request, obj)
    
    has_add_permission = has_change_permission


class EntryNoteAdmin(admin.ModelAdmin):
    fields = [("supplier"), ("charge"), ("carrier", "carrier_price"),("registered"), ("invoice"), "pdf_file" ]
    date_hierarchy = "creation_date"
    list_display = ["pk", "supplier", "tax_amount", "invoice", "registered", "creation_date","pdf_file"]
    search_fields = ["supplier"]
    list_filter = ["registered", "creation_date"]
    readonly_fields = ["invoice", "pdf_file"]

    inlines = [EntryInline]

    def get_readonly_fields(self, request: HttpRequest, obj: Any | None = ...) -> List[str] | Tuple[Any, ...]:
        if obj.invoice:
            return self.readonly_fields + ["supplier", "charge", "carrier", "carrier_price",]
        return super().get_readonly_fields(request, obj)

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        if obj and obj.invoice:
            return False
        return super().has_delete_permission(request, obj)
    
    def has_add_permission(self, request: HttpRequest) -> bool:
        return False


########### INVOICE ############
class EntryNoteInline(admin.TabularInline):
    model = EntryNote
    extra = 0
    fields = EntryNoteAdmin.list_display
    readonly_fields = fields

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def has_add_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


class InvoiceAdmin(admin.ModelAdmin):
    fields = ["supplier", ("serial", "number"), "settlement", "pdf_file"]
    date_hierarchy = "creation_date"
    readonly_fields = ["serial_number", "pdf_file"]
    list_display = ["serial_number", "total_amount", "settlement", "supplier", "creation_date", "pdf_file"]
    list_filter = ["creation_date"]
    list_display_links = ("serial_number", 'settlement', 'supplier')

    inlines = [EntryNoteInline]

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        if obj and obj.settlement:
            return False
        return super().has_change_permission(request, obj)    

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        if obj:
            if obj.settlement:
                return False
            if obj != Invoice.objects.last():
                return False
        return super().has_delete_permission(request, obj)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

########### SETTLEMENT ############
class InvoiceInline(PdfFieldAbstractInline, admin.TabularInline):
    model = Invoice
    extra = 0
    fields = InvoiceAdmin.list_display
    readonly_fields = fields

    def has_change_permission(*args, **kwargs) -> bool:
        return False

    def has_add_permission(*args, **kwargs) -> bool:
        return False

    def has_delete_permission(*args, **kwargs) -> bool:
        return False


class SettlementAdmin(admin.ModelAdmin):
    fields = ["supplier", "pdf_file"]
    date_hierarchy = "creation_date"
    readonly_fields = ["total_amount", "pdf_file"]
    list_display = ["total_amount", "supplier","creation_date", "pdf_file"]
    list_filter = ["creation_date"]
    search_fields = ["supplier"]

    inlines = [InvoiceInline]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False


########### INVOICE ############
class ChargeAdmin(admin.ModelAdmin):
    fieldsets = [("datos",{"fields": [("name")]}), ("gastos", {"fields": ["comision", "descarga", "analisis", "portes", "embalajes"]})]
    list_display = ["name", "comision", "descarga", "analisis", "portes", "embalajes"]



admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(EntryNote, EntryNoteAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Settlement, SettlementAdmin)
admin.site.register(CarrierAgent, CarrierAgentAdmin)
admin.site.register(Charge, ChargeAdmin)
