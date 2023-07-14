from django.db import models

# Create your models here.
from base.models import Agent, AddressAbstract
from product.models import AgrofoodType


class QualityType(models.Model):
    name = models.CharField("nombre", max_length=256)

    class Meta:
        verbose_name = "tipo de calidad"
        verbose_name_plural = "tipos de calidad"

    def __str__(self):
        return self.name


class Land (AddressAbstract, models.Model):
    name = models.CharField("nombre", max_length=256)
    supplier = models.ForeignKey("purchases.Supplier", on_delete=models.CASCADE, verbose_name="Agricultor")

    class Meta:
        verbose_name = "finca"
        verbose_name_plural = "fincas"

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    name = models.CharField("nombre", max_length=256)
    land = models.ForeignKey(Land, on_delete=models.CASCADE, verbose_name="finca")
    quality = models.ForeignKey(QualityType, on_delete=models.PROTECT, verbose_name="calidad")
    agrofoodtypes = models.ManyToManyField(AgrofoodType, verbose_name="tipo de género")

    class Meta:
        verbose_name = "nave"

    def __str__(self):
        return self.name

class Lab(Agent):
    class Meta:
        verbose_name = "Laboratorio"

class Analysis(models.Model):
    date = models.DateField("fecha")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name="Nave", null=True, blank=True)
    entry = models.ForeignKey("purchases.Entry", on_delete=models.PROTECT, verbose_name="Entrada", null=True, blank=True)
    lab = models.ForeignKey(Lab, on_delete=models.PROTECT, verbose_name="laboratorio")

    class Meta:
        verbose_name = "Análisis"
        verbose_name_plural = "Análisis"



