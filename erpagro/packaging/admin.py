from typing import Any

from django.contrib import admin
from django.db.models import Q
from django.http.request import HttpRequest
from django.utils.html import format_html

from .models import Packaging, Transaction, TransactionGroup

class PackagingAdmin(admin.ModelAdmin):
    fields = [("type", "material"), ("name"), ("destare_in", "destare_out"), ("price"), ("total", "min_stock")]
    list_display = ["name", "total", "min_stock", "destare_in", "destare_out", "price"]
    list_filter = ["type", "material"]
    search_fields = ["name"]

class EmptyFilter(admin.SimpleListFilter):
    title = "vacías"
    parameter_name = "empty"

    def lookups(self, request, model_admin):
        return [
            ("true", "Sí"),
            ("false", "No"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "true":
            return queryset.filter(entry__isnull=True, exit__isnull=True)
        if self.value() == "false":
            return queryset.filter(Q(entry__isnull=False)|Q(exit__isnull=False))

class TransactionGroupAdmin(admin.ModelAdmin):
    list_display = ["pk", "creation_date", "agent", "pdf_file"]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
    
    def has_change_permission(self, request: HttpRequest, obj: Any | None = ...) -> bool:
        return False
    
 

class TransactionAdmin(admin.ModelAdmin):
    fields = [("agent", "corrective"),("packaging", "number"), "get_pdf"]
    list_display = ["pk", "packaging", "agent", "number", "creation_date", "entry", "exit", "get_pdf"]
    list_filter = ["creation_date", "packaging__type", "corrective", EmptyFilter]
    search_fields = ["packaging", "agent__name"]
    readonly_fields = ("empty", "get_pdf")

    @admin.display(ordering='creation_date', description='archivo')
    def get_pdf(self, obj):
        pdf_file = None
        if hasattr(obj, "entry"):
            pdf_file = obj.entry.entrynote.pdf_file
        elif hasattr(obj, "exit"): 
            pdf_file = obj.exit.invoice.pdf_file if obj.exit.invoice else None
        elif obj.transaction_group:
            pdf_file = obj.transaction_group.pdf_file 
        return format_html(f"<a href='{pdf_file.url}'>{pdf_file}</a>") if pdf_file else None 
    


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionGroup, TransactionGroupAdmin)
admin.site.register(Packaging, PackagingAdmin)