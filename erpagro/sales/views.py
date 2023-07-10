from django.shortcuts import render

from django.contrib.auth.decorators import permission_required

from purchases.models import Entry
from .models import Client
# Create your views here.


@permission_required(["purchases.view_entry", "purchases.change_exit"])
def listin(request):
    entries = Entry.objects.filter(entrynote__registered=False) #todo: which entries should be displayed
    agrofood_set = set()
    for e in entries:
        agrofood_set.add(e.agrofood)

    if request.method == "GET":
        return render(request, "sales/listin.html", {"aftypes": agrofood_set})

    if request.method == "POST":
        agrofood_pk = request.POST["agrofood-pk"]
        entries = entries.filter(agrofood__pk = agrofood_pk) #todo: which entries should be displayed
        clients = Client.objects.all()
        return render(request, "sales/listin.html", {"entries": entries, 
                                                    "aftypes": agrofood_set,
                                                    "agrofood_pk": agrofood_pk,
                                                    "clients": clients,})