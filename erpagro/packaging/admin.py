from django.contrib import admin

from .models import Packaging, Transaction 

class PackagingAdmin(admin.ModelAdmin):
    fields = [("type", "material"), ("name"), ("destare_in", "destare_out"), ("price"), ("min_stock") ]
    list_display = ["name", "destare_in", "destare_out", "price", "min_stock"]
    list_filter = ["type", "material"]
    search_fields = ["name"]

class TransactionAdmin(admin.ModelAdmin):
    fields = [("agent"),("packaging", "number")]
    list_display = ["packaging", "agent", "number", "creation_date"]
    list_filter = ["creation_date", "packaging__type"]
    search_fields = ["type", "agent"]

admin.site.register(Packaging, PackagingAdmin)
admin.site.register(Transaction, TransactionAdmin)