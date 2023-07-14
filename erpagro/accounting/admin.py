from django.contrib import admin

from .models import Regime
# Register your models here.

class RegimeAdmin(admin.ModelAdmin):
    fields = ("name", "type", "vat", "irpf", "serial")
    list_display = ("name", "serial", "type", "vat", "irpf")
    list_filter = ("type",)

admin.site.register(Regime, RegimeAdmin)