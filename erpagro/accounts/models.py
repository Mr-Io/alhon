from django.db import models

from django.contrib.auth.models import AbstractUser

from purchases.models import Supplier
# Create your models here.

class User(AbstractUser):
    supplier = models.OneToOneField(Supplier, on_delete=models.PROTECT, verbose_name="agricultor", blank=True, null=True)
