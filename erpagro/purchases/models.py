from django.contrib import admin
from django.db import models

from base.models import Agent, EntryExitAbstract
from product.models import AgrofoodType
from quality.models import Warehouse

class ExpenseCarrierPriceAbstract(models.Model):
    carrier_price = models.DecimalField("precio porte", decimal_places=4, max_digits=6, blank=True, null=True)
    class Meta:
        abstract = True

class CarrierAgent(Agent, ExpenseCarrierPriceAbstract):
    class Meta:
        verbose_name = "transportista"

class ExpensesAbstract(ExpenseCarrierPriceAbstract):
    carrier = models.ForeignKey(CarrierAgent, on_delete=models.PROTECT, verbose_name="transportista", blank=True, null=True)
    class Meta:
        abstract = True

class Charge(models.Model):
    name = models.CharField(max_length=256, unique=True, verbose_name="nombre")
    comision = models.DecimalField("COMISIÓN", decimal_places=2, max_digits=4, blank=True, null=True)
    descarga = models.DecimalField("DESCARGA", decimal_places=4, max_digits=6, blank=True, null=True)
    analisis = models.DecimalField("ANÁLISIS", decimal_places=4, max_digits=6, blank=True, null=True)
    portes = models.DecimalField("PORTES", decimal_places=4, max_digits=6, blank=True, null=True)
    embalajes = models.DecimalField("EMBALAJES", decimal_places=4, max_digits=6, blank=True, null=True)

    class Meta:
        verbose_name = "tarifa"
    
    def __str__(self):
        return self.name
    


class SupplierGroup(models.Model):
    name = models.CharField(max_length=256, unique=True, verbose_name="nombre")

    class Meta:
        verbose_name = "agrupación"
        verbose_name_plural = "agrupaciones"

    def __str__(self):
        return self.name

class Supplier(Agent, ExpensesAbstract):
    group = models.ForeignKey(SupplierGroup, on_delete=models.PROTECT, related_name="modules", blank=True, null=True, verbose_name="agrupación")
    share = models.SmallIntegerField("porcentaje de reparto", blank=True, null=True)
    charge = models.ForeignKey(Charge, on_delete=models.PROTECT, verbose_name="tarifa")

    class Meta:
        verbose_name = "agricultor"
        verbose_name_plural = "agricultores"

class Invoice(models.Model):
    settled = models.BooleanField("liquidada", default=False)
    paid = models.BooleanField("pagada", default=False)
    creation_date = models.DateTimeField("fecha", auto_now_add=True)

    class Meta:
        verbose_name = "Factura"

    def __str__(self) -> str:
        return f"{self.pk}"


class EntryNote(ExpensesAbstract):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="entrynotes", verbose_name="agricultor")
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="fecha")
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="entrynotes", blank = True, null=True, verbose_name="factura")
    charge = models.ForeignKey(Charge, on_delete=models.PROTECT, verbose_name="tarifa")

    @admin.display(boolean=True)
    def priced(self):
        return all(x.price_per_kg for x in self.entries.all())

    class Meta:
        verbose_name = "Albarán"
        verbose_name_plural = "Albaranes"

    def __str__(self):
        return f"{self.pk}"

class Entry(EntryExitAbstract):
    entry_note = models.ForeignKey(EntryNote, on_delete=models.CASCADE, related_name="entries", verbose_name="albarán")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="entries", blank=True, null=True, verbose_name="nave")
    agrofood = models.ForeignKey(AgrofoodType, on_delete=models.PROTECT, related_name="entries", verbose_name="género")

    #price - precio total
    @admin.display(description="precio total")
    def total_price(self):
        return self.price * self.weight 

    class Meta:
        verbose_name = "entrada"

