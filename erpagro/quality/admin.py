from django.contrib import admin

from .models import Land, Warehouse, QualityType, Lab, Analysis
# Register your models here.

class LandInline(admin.TabularInline):
    model = Land
    extra = 0

########### CARRIER AGENT ############
class WarehouseInline(admin.TabularInline):
    model = Warehouse
    extra = 0


class LandAdmin(admin.ModelAdmin):
    list_display = ["name", "supplier"]
    inlines = [WarehouseInline]



admin.site.register(Land, LandAdmin)
admin.site.register(QualityType)
admin.site.register(Lab)
admin.site.register(Analysis)