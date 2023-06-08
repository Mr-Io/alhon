from django.contrib import admin

from .models import Land, Warehouse, QualityType
# Register your models here.


admin.site.register(Warehouse)
admin.site.register(QualityType)
admin.site.register(Land)