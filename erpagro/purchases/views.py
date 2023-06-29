import decimal
from utils.func import convert_dotted_json 

from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone


from rest_framework import status

from api.views import EntryDetailSerializer

from django.contrib.auth.decorators import permission_required

from .models import Supplier, CarrierAgent
from packaging.models import Packaging, Transaction
from purchases.models import EntryNote, Entry, Warehouse
from product.models import AgrofoodType
# Create your views here.


@permission_required("purchases.add_entry")
def entry(request):
    suppliers = Supplier.objects.all()
    carriers = CarrierAgent.objects.all()
    boxes = Packaging.objects.filter(type="box")
    pallets = Packaging.objects.filter(type="pallet")

    if request.method == "GET": 
        return render(request, "purchases/entry.html", context={"suppliers": suppliers,
                                                                "carriers": carriers,
                                                                "boxes": boxes,
                                                                "pallets": pallets,})
    if request.method == "POST":
        post = convert_dotted_json(request.POST)
        # get supplier
        try:
            supplier = Supplier.objects.get(pk=post["supplier-pk"])
        except Supplier.DoesNotExist:
            return HttpResponse(f"supplier with id {post['supplier-pk']} does not exist", status=status.HTTP_404_NOT_FOUND)

        # create and save entrynote
        entrynote = EntryNote(supplier=supplier, charge=supplier.charge)
        if post["carrier-pk"]:
            entrynote.carrier = CarrierAgent.objects.get(pk=post["carrier-pk"])
            entrynote.carrier_price = post["carrier-price"]
        entrynote.full_clean()
        entrynote.save()
        # for each entry:
        for _, entry_data in post["entries"].items():
            #create entry
            entry = Entry(entrynote=entrynote)
            entry.warehouse = Warehouse.objects.get(pk=entry_data["warehouse-pk"])
            entry.agrofood = AgrofoodType.objects.get(pk=entry_data["agrofoodtype-pk"])
            entry.weight = decimal.Decimal(entry_data["grossweight"])
            # create box transaction
            box = Packaging.objects.get(pk=entry_data["packaging-pk"])
            trx = Transaction(agent=supplier, packaging=box, number=entry_data["numpackages"])
            trx.full_clean()
            trx.save()
            entry.weight -= trx.packaging.destare_in * trx.number
            entry.packaging_transaction = trx
            # for each pallet
            if "pallets" in entry_data:
                for _, pallet_data in entry_data["pallets"].items():
                    pallet = Packaging.objects.get(pk=pallet_data["pallet-pk"])
                    entry.weight -= pallet.destare_in * decimal.Decimal(pallet_data["numpallets"])
                    # create transaction if pallet stock
                    if pallet.min_stock != "":
                        t = Transaction(agent=supplier, packaging=pallet, number=pallet_data["numpallets"])
                        t.full_clean()
                        t.save()
            entry.weight = round(entry.weight)
            entry.full_clean()
            entry.save()
        #return JsonResponse(post, safe=False)
        return render(request, "purchases/entry.html", context={"suppliers": suppliers,
                                                                "carriers": carriers,
                                                                "boxes": boxes,
                                                                "pallets": pallets,
                                                                "message": f"Entrada de género de {supplier.name} guardada con éxito",})
                                                            

@permission_required("purchases.change_entry")
def entries(request):
    if request.method == "GET":
        entries = Entry.objects.filter(entrynote__invoice__isnull=True)
        return render(request, "purchases/entries.html", {"entries": entries})
    
    if request.method == "POST":
        entries = Entry.objects.filter(Q(pk__in = request.POST.keys()) & Q(price__isnull = False))
        for e in entries:
            entrynote = e.entrynote
            if not entrynote.registered and entrynote.priced():
                entrynote.registered = True
                entrynote.creation_date = timezone.now()
                entrynote.save()
        serializer = EntryDetailSerializer(entries, many=True)
        return JsonResponse(serializer.data, safe=False)