from django.db import models

from base.models import Agent

class Packaging(models.Model):
    name = models.CharField("nombre", max_length=256)
    price = models.DecimalField("precio unitario", decimal_places=2, max_digits=6, blank=True, null=True)  # or float/double field?
    destare_in = models.DecimalField("destare entrada", decimal_places=1, max_digits=4, default=0)  # or float/double field?
    destare_out = models.DecimalField("destare salida", decimal_places=1, max_digits=4, default=0)  # or float/double field?
    min_stock= models.PositiveIntegerField("stock mínimo", blank=True, null=True)
    TYPE_CHOICES =[
        ("plastico","Plástico"),
        ("madera","Madera"),
        ("carton","Cartón"),
        ("ifco","IFCO"),
    ]
    material = models.CharField("material", choices=TYPE_CHOICES, max_length=32)
    TYPE_CHOICES = [("caja", "Caja"),
                    ("pallet", "Pallet")]
    type = models.CharField("tipo", choices=TYPE_CHOICES, max_length=32)
    #stock
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "envase"


class Transaction(models.Model):
    packaging = models.ForeignKey(Packaging, on_delete=models.PROTECT, related_name="transactions", verbose_name="type")
    agent = models.ForeignKey(Agent, on_delete=models.PROTECT, related_name="transactions", verbose_name="agente")
    number = models.BigIntegerField("número")
    creation_date = models.DateTimeField("fecha", auto_now_add=True)

    class Meta:
        verbose_name = "movimiento"