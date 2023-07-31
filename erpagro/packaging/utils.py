from django.db.models import Sum

from .models import Transaction, TransactionGroup

def packaging_balance(agent=None, stock_only=False):
    t = Transaction.objects.all()
    if stock_only:
        t = t.filter(packaging__min_stock__isnull=False)
    if (agent):
        t = t.filter(agent=agent) 
    return t.values("packaging", "packaging__name", "packaging__total").annotate(balance=Sum("number"))

def transaction_group_cleaning():
    for tg in TransactionGroup.objects.filter(transactions__isnull = True):
        tg.delete()
    return