from django.db import models

from base.models import Agent, EntryExitAbstract
from purchases.models import Entry

class ExpenseCommisssionAbstract(models.Model):
    commission = models.DecimalField("COMISIÓN", decimal_places=4, max_digits=6, blank=True, null=True)
    class Meta:
        abstract = True

class CommissionAgent(Agent, ExpenseCommisssionAbstract):
    class Meta:
        verbose_name = "comisionista"

class ExpensesAbstract(ExpenseCommisssionAbstract):
    commission_agent = models.ForeignKey(CommissionAgent, on_delete=models.PROTECT, verbose_name="comisionista", blank=True, null=True)
    rapell = models.DecimalField("RAPELL", decimal_places=4, max_digits=6, blank=True, null=True)
    porte = models.DecimalField("PORTE", decimal_places=4, max_digits=6, blank=True, null=True)
    fianza = models.DecimalField("FIANZA", decimal_places=4, max_digits=6, blank=True, null=True)
    charge = models.DecimalField("Tarifa de gastos", decimal_places=4, max_digits=6, blank=True, null=True)
    class Meta:
        abstract = True

class Client(Agent, ExpensesAbstract):
    class Meta:
        verbose_name = "cliente"

class Invoice(ExpensesAbstract):
    settled = models.BooleanField("liquidada", default=False)
    paid = models.BooleanField("pagada", default=False)
    creation_date = models.DateTimeField("fecha", auto_now_add=True)

    class Meta:
        verbose_name = "factura"

    def __str__(self) -> str:
        return f"Factura {self.pk}"

class Exit(EntryExitAbstract):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="sales",verbose_name="cliente")
    entry = models.ForeignKey(Entry, on_delete=models.PROTECT, related_name="sales", verbose_name="entrada")
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="sales", verbose_name="factura", blank=True, null=True)
    in_warehouse = models.BooleanField("en almacén", default=True)

    class Meta:
        verbose_name = "salida"

    def __str__(self) -> str:
        return f"{self.pk}"
