from django.shortcuts import render
from django.shortcuts import render, get_object_or_404

from django.contrib.auth.decorators import permission_required

from base.models import Agent
from packaging.models import Packaging, Transaction, TransactionGroup
from packaging.utils import packaging_balance
# Create your views here.

def transaction_aux(request, template, sign=1):
    agents = Agent.objects.all()
    packagings =  Packaging.objects.all() # Packaging.objects.filter(min_stock__isnull=False)

    if request.method == "GET":
        return render(request, template, context={"agents": agents,
                                                  "packagings": packagings,})

    if request.method == "POST":
        # get agent and packaging
        agent = get_object_or_404(Agent, pk=request.POST["agent-pk"])
        transaction_group = TransactionGroup(agent=agent)
        transaction_group.full_clean()
        transaction_group.save()
        for pk, num in zip(request.POST.getlist("packaging-pk"), request.POST.getlist("num-packages")):
            if pk:
                packaging = get_object_or_404(Packaging, pk=pk)
                number = sign * int(num)
                trx = Transaction(transaction_group=transaction_group, agent=agent, packaging=packaging, number=number)
                trx.full_clean()
                trx.save()
        transaction_group.full_clean()
        transaction_group.make_pdf()
        return render(request, "packaging/retreat.html", context={"transaction":transaction_group,
                                                                  "agents": agents,
                                                                  "packagings": packagings,
                                                                  "msg": f"Retirada de cajas de {agent.name} guardada con éxito",})

@permission_required("purchases.add_transaction")
def retreat(request):
    return transaction_aux(request, "packaging/retreat.html", sign=-1)

@permission_required("purchases.add_transaction")
def deliver(request):
    return transaction_aux(request, "packaging/deliver.html")


@permission_required("purchases.edit_transaction")
def balance(request):
    agents = Agent.objects.all()

    if request.method == "GET":
        return render(request, "packaging/balance.html", context={"agents": agents,})

    if request.method == "POST":
        agent = get_object_or_404(Agent, pk=request.POST["agent-pk"])
        # check which balances need to be modified
        balances = packaging_balance(agent)
        print(balances)
        transaction_group = TransactionGroup(agent=agent)
        transaction_group.full_clean()
        transaction_group.save()
        for b in balances:
            # make a corrective transaction and update the new total number of actives
            new_balance = int(request.POST.get(str(b["packaging"]), None))
            diff = new_balance - b["balance"]
            if diff:
                print("new_balance", new_balance)
                print("post", request.POST)
                print("diff", diff)
                # update total active at company level
                p = get_object_or_404(Packaging, pk=b["packaging"])
                p.total += diff
                p.full_clean()
                p.save()
                # make a corrective transaction
                trx = Transaction(transaction_group=transaction_group, packaging=p, agent=agent, number=diff, corrective=True)
                trx.full_clean()
                trx.save()
        # print new balances
        transaction_group.full_clean()
        transaction_group.make_pdf()
        print("transaction_group", transaction_group)
        print("transaction_group.pdf_file", transaction_group.pdf_file)
        print("transaction_group.pdf_file.url", transaction_group.pdf_file.url)
        return render(request, "packaging/balance.html", context={"new_page_anchor": transaction_group.pdf_file.url,
                                                                  "agents": agents,
                                                                  "msg": f"Actualizado saldo de {agent.name}",})

@permission_required("purchases.view_transaction")
def stock(request):
    balances = packaging_balance()

    if request.method == "GET":
        return render(request, "packaging/stock.html", context={"balances": balances,})
