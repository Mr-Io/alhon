from django.contrib import admin
from django.utils.html import format_html

class PdfFieldAbstractAdmin(admin.ModelAdmin):

    def pdflink(self, instance):
        return format_html(f'<a href="{instance.doc_link}" target=_blank>&#128196</a>', url=instance.doc_link) if instance.doc_link else None
    pdflink.short_description = "doc"

    class Meta:
        abstract = True


class PdfFieldAbstractInline(admin.TabularInline):

    def pdflink(self, instance):
        return format_html(f'<a href="{instance.doc_link}" target=_blank>&#128196</a>', url=instance.doc_link) if instance.doc_link else None
    pdflink.short_description = "doc"

    class Meta:
        abstract = True

