from django.db import models

from packaging.models import Packaging

class AgrofoodFamily(models.Model):
    name = models.CharField(max_length=256, unique=True, verbose_name="nombre")

    class Meta:
        verbose_name = "familia género"
        verbose_name_plural = "familias género"

    def __str__(self):
        return self.name

class AgrofoodSubfamily(models.Model):
    name = models.CharField(max_length=256, verbose_name="nombre")
    family = models.ForeignKey(AgrofoodFamily, on_delete=models.CASCADE, verbose_name="familia")

    class Meta:
        verbose_name = "subfamilia género"
        verbose_name_plural = "subfamilias género"

    def __str__(self):
        return self.name

class AgrofoodType(models.Model):
    name = models.CharField("nombre", max_length=256)
    subfamily = models.ForeignKey(AgrofoodSubfamily, on_delete=models.CASCADE, verbose_name="subfamilia")
    price_min = models.DecimalField("precio mín. coste", decimal_places=2, max_digits=6, blank=True, null=True)  # or float/double field?
    packaging = models.ForeignKey(Packaging, on_delete=models.PROTECT, verbose_name="envase", null=True)
    QUALITY_CHOICES = [
        ("I", "Primera"),
        ("II", "Segunda"),
        ("AVENADO", "Avenado")
    ]
    quality = models.CharField("calidad", choices=QUALITY_CHOICES, max_length=8)

    class Meta:
        verbose_name = "tipo de género"
        verbose_name_plural = "tipos de género"

    def __str__(self):
        return f"{self.name} {self.quality if self.quality else ''}"