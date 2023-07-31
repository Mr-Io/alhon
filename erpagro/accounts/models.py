from django.db import models

from django.contrib.auth.models import AbstractUser

from base.models import Agent
# Create your models here.

class User(AbstractUser):
    agent = models.OneToOneField(Agent, on_delete=models.PROTECT, verbose_name="agente", blank=True, null=True)

    class Meta:
        verbose_name = "usuario"

class Company(Agent):
    id_unique = models.CharField(primary_key=True, default="setting", max_length=7)
    tax_start = models.DateField("inicio fiscal")
    post_box = models.CharField("apdo. correos", max_length=2, blank=True)
    address_line2 = models.CharField("línea extra dirección", max_length=46, blank=True)
    invoice_line = models.TextField("línea extra factura", max_length=182, blank=True)

    def serial(self):
        return f"{self.tax_start.year % 100}"

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Datos Empresa"



