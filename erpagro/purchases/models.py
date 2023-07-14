from decimal import Decimal

from django.contrib import admin
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

from accounting.models import TaxesAbstract, Regime
from base.models import Agent, EntryExitAbstract
from product.models import AgrofoodType
from quality.models import Warehouse
from accounts.models import Company
from archive.models import MakeFileAbstract


class CarrierPriceAbstract(models.Model):
    carrier_price = models.DecimalField("precio porte", decimal_places=4, max_digits=6, blank=True, null=True, validators=[MinValueValidator(0.0001)])
    class Meta:
        abstract = True

class CarrierAgent(Agent, CarrierPriceAbstract):
    class Meta:
        verbose_name = "transportista"

class CarrierAbstract(models.Model):
    carrier = models.ForeignKey(CarrierAgent, on_delete=models.PROTECT, verbose_name="transportista", blank=True, null=True)
    class Meta:
        abstract = True
    
class ExpensesAbstract(models.Model):
    comision = models.DecimalField("COMISIÓN", decimal_places=4, max_digits=6, blank=True, null=True, validators=[MinValueValidator(0.0001)])
    descarga = models.DecimalField("DESCARGA", decimal_places=4, max_digits=6, blank=True, null=True, validators=[MinValueValidator(0.0001)])
    analisis = models.DecimalField("ANÁLISIS", decimal_places=4, max_digits=6, blank=True, null=True, validators=[MinValueValidator(0.0001)])
    portes = models.DecimalField("PORTES", decimal_places=4, max_digits=6, blank=True, null=True, validators=[MinValueValidator(0.0001)])
    embalajes = models.DecimalField("EMBALAJES", decimal_places=4, max_digits=6, blank=True, null=True, validators=[MinValueValidator(0.0001)])

    class Meta:
        abstract = True


class Charge(ExpensesAbstract):
    name = models.CharField(max_length=64, unique=True, verbose_name="nombre")

    class Meta:
        verbose_name = "tarifa"
    
    def __str__(self):
        return self.name
    

class SupplierGroup(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name="nombre")

    class Meta:
        verbose_name = "agrupación"
        verbose_name_plural = "agrupaciones"

    def __str__(self):
        return self.name


class Supplier(Agent, CarrierAbstract):
    group = models.ForeignKey(SupplierGroup, on_delete=models.PROTECT, blank=True, null=True, verbose_name="agrupación")
    charge = models.ForeignKey(Charge, on_delete=models.PROTECT, verbose_name="tarifa")
    regime = models.ForeignKey(Regime, on_delete=models.PROTECT, verbose_name="régimen")

    def has_view_permission(self, request):
        
        return hasattr(self, "user") and self.user == request.user

    class Meta:
        verbose_name = "agricultor"
        verbose_name_plural = "agricultores"


class Settlement(MakeFileAbstract, models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    creation_date = models.DateTimeField("fecha", auto_now_add=True)

    def clean(self):
        if self.pk:
            if not self.invoice_set.exists():
                raise ValidationError("Liquidación sin facturas")
            for i in self.invoice_set.all():
                if i.supplier != self.supplier:
                    raise ValidationError({"supplier": f"Liquidación {self} a agricultor {self.supplier} con factura {i} a agricultor {i.supplier}"})
        return super().clean()

    @admin.display(description="nº serie")
    def serial_number(self):
        return f"{self.pk:08}"

    def carrier_expense(self):
        return sum(i.carrier_expense() for i in self.invoice_set.all())
    
    def expenses(self):
        return sum(i.expenses() for i in self.invoice_set.all())
    
    def base_amount(self):
        return sum(i.base_amount() for i in self.invoice_set.all())
    
    def expenses_amount(self):
        return sum(i.expenses_amount() for i in self.invoice_set.all())

    def tax_amount(self):
        return sum(i.tax_amount() for i in self.invoice_set.all())
    
    def vat_amount(self):
        return sum(i.vat_amount() for i in self.invoice_set.all())
    
    def irpf_amount(self):
        return sum(i.irpf_amount() for i in self.invoice_set.all())

    @admin.display(description="importe total")
    def total_amount(self):
        return sum(i.total_amount() for i in self.invoice_set.all())
   
    class Meta:
        verbose_name = "liquidación"
        verbose_name_plural = "liquidaciones"

    def __str__(self) -> str:
        return f"{self.pk}"



class Invoice(MakeFileAbstract, TaxesAbstract):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    number = models.PositiveSmallIntegerField("número", blank=True, null=True)
    creation_date = models.DateTimeField("fecha", auto_now_add=True)
    settlement = models.ForeignKey(Settlement, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="liquidación")
 
    def clean(self):
        if self.pk:
            if not self.entrynote_set.exists():
                raise ValidationError("Factura sin albaranes")
            for en in self.entrynote_set.all():
                if not en.priced():
                    raise ValidationError(f"Albarán {en} no valorado")
                if self.supplier != en.supplier:
                    raise ValidationError({"supplier": f"factura {self} a agricultor {self.supplier} con albarán {en} a agricultor {en.supplier}"})
        return super().clean()

    def save(self, *args, **kwargs):
        if not self.serial:
            self.serial = f"{Company.objects.first().tax_start.year % 100 + 1}{self.supplier.regime.serial}"
        if not self.number:
            n_previous_invoices = Invoice.objects.filter(serial = self.serial).count()
            self.number = 1 + n_previous_invoices 
        if not self.vat:
            self.vat = self.supplier.regime.vat
        if not self.irpf:
            self.irpf = self.supplier.regime.irpf
        if not self.type:
            self.type = self.supplier.regime.type
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.pdf_file.delete(save=False)
        return super().delete(*args, **kwargs)

    def carrier_expense(self):
        return sum(en.carrier_expense() for en in self.entrynote_set.all())
    
    def expenses(self):
        return sum(en.expenses() for en in self.entrynote_set.all())
    
    @admin.display(description="nº serie")
    def serial_number(self):
        return f"{self.serial}-{self.number:05}"

    def base_amount(self):
        return sum(en.base_amount() for en in self.entrynote_set.all())
    
    def expenses_amount(self):
        return sum(en.expenses_amount() for en in self.entrynote_set.all())

    def tax_amount(self):
        return sum(en.tax_amount() for en in self.entrynote_set.all())
    
    def vat_amount(self):
         return round(self.vat/Decimal("100") * self.tax_amount(), 2)
    
    def irpf_amount(self):
        if self.type == "E":
            base_value = self.tax_amount() + self.vat_amount()
        elif self.type == "G":
            base_value = self.tax_amount()
        return round(base_value * self.irpf/Decimal("100"), 2)

    @admin.display(description="importe total")
    def total_amount(self):
        return self.tax_amount() + self.vat_amount() - self.irpf_amount()
   
    class Meta:
        verbose_name = "factura"

    def __str__(self) -> str:
        return f"{self.serial_number()}"

class EntryNote(CarrierAbstract, CarrierPriceAbstract, ExpensesAbstract, MakeFileAbstract):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name="agricultor")
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, blank = True, null=True, verbose_name="factura")
    charge = models.ForeignKey(Charge, on_delete=models.PROTECT, verbose_name="tarifa")
    registered = models.BooleanField("registrado", default=False)
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="fecha")

    class Meta:
        verbose_name = "Albarán"
        verbose_name_plural = "Albaranes"

    def clean(self):
        if self.registered:
            if not self.pk:
                raise ValidationError({"registered": "No se puede añadir directamente un albarán registrado"})
            if not self.entry_set.exists():
                raise ValidationError({"registered": "albarán sin entradas"})
            if not self.priced():
                raise ValidationError({"registered":"albarán no valorado"})
            if self.pending(): 
                raise ValidationError({"registered":"kg de alguna entrada sin vender"}) 
            if not self.all_exit_priced():
                raise ValidationError({"registered":"kg de alguna entrada sin precio de venta"})
            if not self.sent():
                raise ValidationError({"registered":"kg de alguna entrada todavía en almacén"})
        if self.pk:
            if not self.entry_set.exists():
                raise ValidationError("Albarán sin entradas")
        return super().clean()
 
    def save(self, *args, **kwargs):
        self.comision = self.charge.comision
        self.descarga = self.charge.descarga
        self.analisis = self.charge.analisis
        self.portes = self.charge.portes
        self.embalajes = self.charge.embalajes
        return super().save(*args, **kwargs)
    
    def serial_number(self):
        return f"{self.pk:08}"
    
    def weight(self):
        return sum(e.weight for e in self.entry_set.all())

    def packages(self):
        return sum(e.packaging_transaction.number for e in self.entry_set.all())

    @admin.display(description="importe bruto")
    def base_amount(self):
        if self.priced():
            return sum(e.base_amount() for e in self.entry_set.all())
        return None

    @admin.display(description="gasto")
    def expenses(self):
        amount = self.base_amount()
        num_packages = self.packages()
        kg_weight = self.weight()
        expense = Decimal("0.00") 
        expense += round(amount*self.comision, 2) if self.comision else Decimal("0.00")
        expense += round(kg_weight*self.descarga, 2) if self.descarga else Decimal("0.00")
        expense += round(kg_weight*self.analisis, 2) if self.analisis else Decimal("0.00")
        expense += round(kg_weight*self.portes, 2) if self.portes else Decimal("0.00")
        expense += round(num_packages*self.embalajes, 2) if self.embalajes else Decimal("0.00")
        return expense

    @admin.display(description="porte")
    def carrier_expense(self):
        return round(self.carrier_price * self.weight(), 2) if self.carrier_price else Decimal("0.00")
    
    @admin.display(description="importe neto")
    def tax_amount(self):
        if self.priced():
            return self.base_amount() - self.expenses() - self.carrier_expense()
        return None 
    
    @admin.display(boolean=True, description="valorado")
    def priced(self):
        return all(e.price for e in self.entry_set.all())
    
    def all_exit_priced(self):
        return all(e.all_exit_priced() for e in self.entry_set.all())

    def pending(self):
        return sum(e.pending() for e in self.entry_set.all())
    
    def sent(self):
        return sum(e.sent() for e in self.entry_set.all())
    

    def __str__(self):
        return f"{self.pk}"

class Entry(EntryExitAbstract):
    entrynote = models.ForeignKey(EntryNote, on_delete=models.CASCADE, verbose_name="albarán")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name="nave")
    agrofood = models.ForeignKey(AgrofoodType, on_delete=models.PROTECT, verbose_name="género")

    def clean(self) -> None:
        if self.agrofood not in self.warehouse.agrofoodtypes.all():
            raise ValidationError({"agrofood": f"{self.agrofood} no está disponible para la nave {self.warehouse}"})
        return super().clean()

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

    @admin.display(description="enviado")
    def sent(self):
        return sum(exit.weight if exit.sent else 0 for exit in self.exit_set.all())
    
    class Meta:
        verbose_name = "entrada"
