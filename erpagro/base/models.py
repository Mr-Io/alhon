from django.db import models

# Create your models here.
class Agent(models.Model):
    name = models.CharField(max_length=256, unique=True, verbose_name="nombre")
    cif = models.CharField(max_length=16, blank=True, verbose_name="cif/nif")
    address = models.CharField(max_length=256, blank=True, verbose_name="dirección")
    #city?
    #state1? comunidad
    #state2? provincia
    #country
    phone = models.CharField(max_length=64, blank=True, verbose_name="teléfono")
    mobile = models.CharField(max_length=64, blank=True, verbose_name="móvil")
    email = models.EmailField(blank=True, null=True)
    fax = models.CharField(max_length= 64, blank=True)
    # contactos
    # tipo proveedor
    # Empresa + punto de venta

    def __str__(self):
        return self.name

class Contact(Agent):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="contacts")

    class Meta:
        verbose_name = "contacto"


class EntryExitAbstract(models.Model):
    weight = models.DecimalField("peso neto", decimal_places=0, max_digits=8)
    price = models.DecimalField("precio por kg", decimal_places=4, max_digits=8, blank=True, null=True)
    creation_date = models.DateTimeField("fecha", auto_now_add=True)
    packaging_transaction = models.OneToOneField("packaging.Transaction", on_delete=models.PROTECT)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"{self.pk}"