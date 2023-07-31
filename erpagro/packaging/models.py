from django.db import models
from django.contrib import admin
from django.core.exceptions import ValidationError

from archive.models import MakeFileAbstract
from base.models import Agent 

class Packaging(models.Model):
    name = models.CharField("nombre", max_length=256)
    price = models.DecimalField("precio unitario", decimal_places=2, max_digits=6, blank=True, null=True)  # or float/double field?
    destare_in = models.DecimalField("destare entrada", decimal_places=1, max_digits=4, default=0)  # or float/double field?
    destare_out = models.DecimalField("destare salida", decimal_places=1, max_digits=4, default=0)  # or float/double field?
    min_stock= models.PositiveIntegerField("stock mínimo", blank=True, null=True)
    total = models.PositiveIntegerField("total", default=0)
    MATERIAL_CHOICES =[
        ("plastico","Plástico"),
        ("madera","Madera"),
        ("carton","Cartón"),
        ("ifco","IFCO"),
    ]
    material = models.CharField("material", choices=MATERIAL_CHOICES, max_length=32)
    TYPE_CHOICES = [("box", "Caja"),
                    ("pallet", "Pallet")]
    type = models.CharField("tipo", choices=TYPE_CHOICES, max_length=32)

    #stock
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "envase"


class TransactionGroup(MakeFileAbstract):
    agent = models.ForeignKey(Agent, on_delete=models.PROTECT, verbose_name="agente")
    creation_date = models.DateTimeField("fecha", auto_now_add=True)

    def clean(self):
        if self.pk:
            for t in self.transaction_set.all():
                if t.agent != self.agent:
                    raise ValidationError({"TransactionGroup": f"Grupo de movimiento de cajas {self} del agente {self.agent} con movimiento {t} a agente {t.agent}"})
        return super().clean()


    def serial_number(self):
        return f"{self.pk:08}"

    def __str__(self):
        return f"TransactionGroup-{self.pk}"

    class Meta:
        verbose_name = "archivos pdf"


class Transaction(models.Model):
    transaction_group = models.ForeignKey(TransactionGroup, on_delete=models.CASCADE, verbose_name="archivos", blank=True, null=True)
    packaging = models.ForeignKey(Packaging, on_delete=models.PROTECT, related_name="transactions", verbose_name="tipo")
    agent = models.ForeignKey(Agent, on_delete=models.PROTECT, related_name="transactions", verbose_name="agente")
    number = models.BigIntegerField("número")
    creation_date = models.DateTimeField("fecha", auto_now_add=True)
    corrective = models.BooleanField("corrección saldo", default=False)

    @admin.display(description="saldo")
    def balance(self):
        return self.__class__.objects.filter(agent=self.agent, packaging=self.packaging, creation_date__lte=self.creation_date).aggregate(models.Sum("number"))["number__sum"]

    @admin.display(description="vacias", boolean=True)
    def empty(self):
        return not (hasattr(self, "entry") or hasattr(self, "exit"))

    def serial_number(self):
        return f"{self.pk:08}"

    def __str__(self):
        return f"{'+' if self.number > 0 else ''}{self.number} {self.packaging.name}"

    class Meta:
        verbose_name = "movimiento"