from django.contrib import admin
from django.db import models
from django.core.exceptions import ValidationError

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

class ExpensesAbstract(models.Model):
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

    def is_this_user(self, user):
        if not hasattr(self, "user"):
            return False
        return self.user == user

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


class EntryNote(ExpensesAbstract, ExpenseCarrierPriceAbstract):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="entrynotes", verbose_name="agricultor")
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="fecha")
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="entrynotes", blank = True, null=True, verbose_name="factura")
    charge = models.ForeignKey(Charge, on_delete=models.PROTECT, verbose_name="tarifa")
    registered = models.BooleanField("registrado", default=False)

    def save(self, *args, **kwargs):
        if self.registered:
            if not self.priced():
                raise ValidationError("Intento de registro de albarán sin valorar")
            if self.pending(): 
                raise ValidationError("Intento de registro de albarán con kg de alguna entrada sin vender") 
            if not self.all_exit_priced():
                raise ValidationError("Intento de registro de albarán con kg de alguna entrada sin precio de venta")
            if self.in_warehouse():
                raise ValidationError("Intento de registro de albarán con kg de alguna entrada todavía en almacén")
        return super().save(*args, **kwargs)

    @admin.display(boolean=True, description="valorado")
    def priced(self):
        return all(e.price for e in self.entry_set.all())
    
    @admin.display(boolean=True, description="vendido")
    def all_exit_priced(self):
        return all(e.all_exit_priced() for e in self.entry_set.all())

    def pending(self):
        return sum(e.pending() for e in self.entry_set.all())
    
    def in_warehouse(self):
        return sum(e.in_warehouse() for e in self.entry_set.all())

    class Meta:
        verbose_name = "Albarán"
        verbose_name_plural = "Albaranes"

    def __str__(self):
        return f"{self.pk}"

class Entry(EntryExitAbstract):
    entrynote = models.ForeignKey(EntryNote, on_delete=models.CASCADE, verbose_name="albarán")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, blank=True, null=True, verbose_name="nave")
    agrofood = models.ForeignKey(AgrofoodType, on_delete=models.PROTECT, verbose_name="género")

    #price - precio total
    @admin.display(description="precio total")
    def total_price(self):
        return self.price * self.weight if self.price else "-"
    
    @admin.display(description="sin vender")
    def pending(self, ignore=None):
        exits = self.exit_set.exclude(pk=ignore.pk) if ignore else self.exit_set.all()
        return self.weight - sum(exit.weight for exit in exits)
    
    @admin.display(description="bultos pendientes")
    def pending_packages(self):
        return self.packaging_transaction.number + sum(exit.packaging_transaction.number for exit in self.exit_set.all())
    
    @admin.display(description="vendido con precio")
    def all_exit_priced(self):
        return all(e.price for e in self.exit_set.all())

    @admin.display(description="en almacén")
    def in_warehouse(self):
        return self.weight - sum(exit.weight if not exit.in_warehouse else 0 for exit in self.exit_set.all())
    
    class Meta:
        verbose_name = "entrada"

