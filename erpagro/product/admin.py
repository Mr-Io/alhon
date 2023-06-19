from django.contrib import admin

from .models import AgrofoodFamily, AgrofoodType, AgrofoodSubfamily

########### AGROFOOD TYPE ############
class AgrofoodTypeAdmin(admin.ModelAdmin):
    fields = [("subfamily"), ("name", "quality"), ("packaging"), "price_min"]
    list_display = ["__str__", "quality", "price_min"]
    list_filter = ["subfamily__family", "quality"]
    search_fields = ["name"]

########### AGROFOOD SUBFAMILY ############
class AgrofoodTypeInline(admin.TabularInline):
    model = AgrofoodType
    fields = AgrofoodTypeAdmin.fields
    extra = 0

class AgrofoodSubfamilyAdmin(admin.ModelAdmin):
    fields = ["family", "name"]
    list_display = ["name"]
    search_fields = list_display
    list_filter = ["family"]

    inlines = [AgrofoodTypeInline]

########### AGROFOOD FAMILY ############

class AgrofoodSubfamilyInline(admin.TabularInline):
    model = AgrofoodSubfamily
    extra = 0

class AgrofoodFamilyAdmin(admin.ModelAdmin):
    fields = ["name"]
    list_display = ["name"]
    search_fields = list_display

    inlines = [AgrofoodSubfamilyInline]

admin.site.register(AgrofoodFamily, AgrofoodFamilyAdmin)
admin.site.register(AgrofoodSubfamily, AgrofoodSubfamilyAdmin)
admin.site.register(AgrofoodType, AgrofoodTypeAdmin)



