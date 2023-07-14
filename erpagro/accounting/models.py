from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class TaxesAbstract(models.Model):
    CHOICES_TYPE = [
       ("G", "Reg. General"),
       ("E", "Reg. Esp. Agrario"),
    ]
    type = models.CharField("tipo", max_length=1, choices=CHOICES_TYPE)
    vat = models.DecimalField("%IVA", max_digits=4, decimal_places=2)
    irpf = models.DecimalField("%IRPF", max_digits=4, decimal_places=2)
    serial = models.CharField("serie", max_length=10, blank=True, null=True)

    class Meta:
        abstract = True


class Regime(TaxesAbstract):
    name = models.CharField("nombre", max_length=64, unique=True)
    def clean(self) -> None:
        if not self.serial:
            raise ValidationError({"serial": "La serie debe especificarse"})
        return super().clean()
    # cuenta suministros, anticipos, efectos, compras, iva_albaran, iva_factura, iva_liquido, retención

    class Meta:
        verbose_name = "Régimen"
        verbose_name_plural = "Regímenes"

    def __str__(self):
        return self.name