from django.apps import AppConfig
from django.db.models.signals import post_delete

def delete_transaction(sender, instance, using, origin, **kwargs):
    print(sender, instance, using, origin)
    instance.packaging_transaction.delete()


class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'

    def ready(self):
        post_delete.connect(delete_transaction, "purchases.Entry")

