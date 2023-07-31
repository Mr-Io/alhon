import datetime
import decimal
from utils.func import convert_dotted_json

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_date

from rest_framework import status

from django.contrib.auth.decorators import permission_required

from .models import Supplier, CarrierAgent
from packaging.models import Packaging, Transaction
from purchases.models import EntryNote, Entry, Warehouse, Invoice, Settlement
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
                                                                "pallets": pallets, })
    if request.method == "POST":
        post = convert_dotted_json(request.POST)
        # get supplier
        supplier = get_object_or_404(Supplier, pk=post["supplier-pk"])
        # create and save entrynote
        entrynote = EntryNote(supplier=supplier, charge=supplier.charge)
        if post["carrier-pk"]:
            entrynote.carrier = CarrierAgent.objects.get(pk=post["carrier-pk"])
            entrynote.carrier_price = post["carrier-price"]
        entrynote.full_clean() # only field-lvl constrainst are checked since it has not been saved yet
        entrynote.save()
        # for each entry:
        for _, entry_data in post["entries"].items():
            # create entry
            entry = Entry(entrynote=entrynote)
            entry.warehouse = Warehouse.objects.get(pk=entry_data["warehouse-pk"])
            entry.agrofood = AgrofoodType.objects.get(pk=entry_data["agrofoodtype-pk"])
            entry.weight = decimal.Decimal(entry_data["grossweight"])
            # create box transaction
            box = Packaging.objects.get(pk=entry_data["packaging-pk"])
            trx = Transaction(agent=supplier, packaging=box, number=entry_data["numpackages"])
            trx.full_clean() # check field-lvl constraints
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
            entry.full_clean() # check field-lvl constraints
            entry.save()
        entrynote.full_clean() # check relation-lvl constraints 
        entrynote.make_pdf()
        return render(request, "purchases/entry.html", context={"entrynote": entrynote,
                                                                "suppliers": suppliers,
                                                                "carriers": carriers,
                                                                "boxes": boxes,
                                                                "pallets": pallets,
                                                                "msg": f"Entrada de género de {supplier.name} guardada con éxito", })


@permission_required("purchases.change_entry")
def entries(request):
    if request.method == "GET":
        entries = Entry.objects.filter(entrynote__invoice__isnull=True)
        return render(request, "purchases/entries.html", {"entries": entries})


@permission_required("purchases.add_invoice")
def selfbilling(request):
    # if dates in query -> get list of entrynotes and suppliers ready to invoice 
    datefrom = parse_date(request.GET["datefrom"]) if "datefrom" in request.GET else datetime.date(year=2022, month=9, day=1)
    dateto = parse_date(request.GET["dateto"]) if "dateto" in request.GET else datetime.datetime.now().date()
    if datefrom and dateto:
        entrynotes = EntryNote.objects.filter(
            creation_date__date__gte=datefrom,
            creation_date__date__lte=dateto,
            invoice__isnull = True,
            ).exclude(
            entry__price__isnull=True,
            )
    else:
        entrynotes = EntryNote.objects.none()

    suppliers = Supplier.objects.filter(entrynote__in = entrynotes).distinct()

    # if supplier in query -> get supplier and update entrynotes
    if "supplier" in request.GET:
        supplier_pk = request.GET["supplier"]
        supplier = get_object_or_404(Supplier, pk=supplier_pk)
        entrynotes = entrynotes.filter(supplier=supplier)
    else:
        supplier_pk = None
        supplier = None
        entrynotes = EntryNote.objects.none()


    if request.method == "GET":
        return render(request, "purchases/selfbilling.html", {"datefrom": datefrom,
                                                              "dateto": dateto,
                                                              "suppliers": suppliers,
                                                              "supplier_pk": supplier_pk,
                                                              "entrynotes": entrynotes,})
    if request.method == "POST":
        # save new invoice
        post = convert_dotted_json(request.POST)
        entrynote_set = EntryNote.objects.filter(id__in = post["entrynotes"])
        if any(en.invoice for en in entrynote_set.all()):
            return HttpResponse(f"error: algún albarán ya ha sido facturado previamente", status=status.HTTP_406_NOT_ACCEPTABLE)
        invoice = Invoice.objects.create(supplier=supplier)
        invoice.entrynote_set.add(*entrynote_set)
        invoice.make_pdf()
        invoice.full_clean() # check field and relation lvl constraints

        return render(request, "purchases/selfbilling.html", {"invoice": invoice,
                                                              "msg": "Autofactura generada y guardada con éxito",
                                                              "datefrom": datefrom,
                                                              "dateto": dateto,
                                                              "suppliers": suppliers,
                                                              "supplier_pk": supplier_pk,
                                                              "entrynotes": entrynotes,})

@permission_required("purchases.add_settlement")
def settle(request):
    # if dates in query -> get list of entrynotes and suppliers ready to invoice 
    datefrom = parse_date(request.GET["datefrom"]) if "datefrom" in request.GET else datetime.date(year=2022, month=9, day=1)
    dateto = parse_date(request.GET["dateto"]) if "dateto" in request.GET else datetime.datetime.now().date()
    if datefrom and dateto:
        invoices = Invoice.objects.filter(
            creation_date__date__gte=datefrom,
            creation_date__date__lte=dateto,
            settlement__isnull = True,
            )
    else:
        invoices = Invoice.objects.none()

    suppliers = Supplier.objects.filter(entrynote__invoice__in = invoices).distinct()

    # if supplier in query -> get supplier and update entrynotes
    if "supplier" in request.GET:
        supplier_pk = request.GET["supplier"]
        supplier = get_object_or_404(Supplier, pk=supplier_pk)
        invoices = invoices.filter(supplier=supplier)
    else:
        supplier_pk = None
        supplier = None
        invoices = EntryNote.objects.none()

    if request.method == "GET":
        return render(request, "purchases/settle.html", {"datefrom": datefrom,
                                                         "dateto": dateto,
                                                         "suppliers": suppliers,
                                                         "supplier_pk": supplier_pk,
                                                         "invoices": invoices,})
    if request.method == "POST":
        # save new invoice
        post = convert_dotted_json(request.POST)
        invoice_set= Invoice.objects.filter(id__in = post["invoices"])
        if any(i.settlement for i in invoice_set.all()):
            return HttpResponse("error: las facturas ya han sido liquidadas previamente", status=status.HTTP_406_NOT_ACCEPTABLE)
        settlement = Settlement.objects.create(supplier=supplier)
        settlement.invoice_set.add(*invoice_set)
        settlement.make_pdf()
        settlement.full_clean()

        return render(request, "purchases/settle.html", {"settlement": settlement,
                                                         "msg": "Liquidación generada y guardada con éxito",
                                                         "datefrom": datefrom,
                                                         "dateto": dateto,
                                                         "suppliers": suppliers,
                                                         "supplier_pk": supplier_pk,
                                                         "invoices": invoices,})