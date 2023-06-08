from django.db import models

# Create your models here.
from product.models import AgrofoodType


class QualityType(models.Model):
    value = models.PositiveSmallIntegerField(unique=True)

    class Meta:
        verbose_name = "tipo de calidad"
        verbose_name_plural = "tipos de calidad"

    def __str__(self):
        return f"nivel de calidad: {self.value}"



class Land (models.Model):
    name = models.CharField("nombre", max_length=256)
    supplier = models.ForeignKey("purchases.Supplier", on_delete=models.CASCADE, related_name="lands", verbose_name="Agricultor")

    class Meta:
        verbose_name = "finca"
        verbose_name_plural = "fincas"

    def __str__(self):
        return self.name



class Warehouse(models.Model):
    name = models.CharField("nombre", max_length=256)
    land = models.ForeignKey(Land, on_delete=models.CASCADE, related_name="warehouses", verbose_name="finca")
    quality = models.ForeignKey(QualityType, on_delete=models.PROTECT, related_name="warehouses", verbose_name="calidad")
    agrofood_types = models.ManyToManyField(AgrofoodType, related_name="warehouses", verbose_name="tipo de género")

    class Meta:
        verbose_name = "nave"
        verbose_name_plural = "naves"

    def __str__(self):
        return self.name



