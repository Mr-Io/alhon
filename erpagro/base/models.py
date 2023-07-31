from django.db import models
from django.contrib import admin
from django.core.validators import MinValueValidator

############# ABSTRACT BASE CLASSES ##############
class AddressAbstract(models.Model):
    COUNTRY_CHOICES = [
        ("ES", "ESPAÑA"),
        ("PT", "PORTUGAL"),
        ("IT", "ITALIA"),
    ]
    country = models.CharField("país", choices=COUNTRY_CHOICES, max_length=2, blank=True)
    postal_code = models.CharField("código postal", max_length=5, blank=True)
    state = models.CharField("provincia", max_length=30, blank=True)
    city = models.CharField("población", max_length=30, blank=True)
    address_line = models.CharField("dirección", max_length=46, blank=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"{self.pk}"

class BaseAgentAbstract(models.Model):
    name = models.CharField("nombre", max_length=64, unique=True) 
    mobile = models.CharField("telf. móvil", max_length=32, blank=True)
    email = models.EmailField(blank=True, null=True)

    def is_user_from(self, request):
        return hasattr(self, "user") and self.user == request.user

    class Meta:
        abstract = True


############# BASE CLASSES ##############
class Agent(BaseAgentAbstract, AddressAbstract):
    cif = models.CharField("cif/nif", max_length=16, blank=True)
    phone = models.CharField("teléfono", max_length=64, blank=True)
    fax = models.CharField(max_length= 64, blank=True)

    def __str__(self):
        return self.name

class Contact(BaseAgentAbstract):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "contacto"


class EntryExitAbstract(models.Model):
    weight = models.DecimalField("peso neto", decimal_places=0, max_digits=8, validators=[MinValueValidator(1)])
    price = models.DecimalField("precio", decimal_places=2, max_digits=6, blank=True, null=True, validators=[MinValueValidator(0.01)])
    creation_date = models.DateTimeField("fecha", auto_now_add=True)
    packaging_transaction = models.OneToOneField("packaging.Transaction", on_delete=models.PROTECT, verbose_name="Envases")

    #price - precio total
    @admin.display(description="importe")
    def base_amount(self):
        return self.price * self.weight if self.price else None

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"{self.pk}"