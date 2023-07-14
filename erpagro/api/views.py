from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.urls import reverse, resolve
from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination

from product.models import AgrofoodType
from purchases.models import Supplier, CarrierAgent, Entry, EntryNote, Invoice
from quality.models import Warehouse
from sales.models import Exit

from .serializers import SupplierListSerializer, SupplierDetailSerializer, WarehouseDetailSerializer, AgrofoodTypeDetailSerializer, CarrierAgentDetailSerializer, EntryDetailSerializer, ExitDetailSerializer, EntryNoteListSerializer

from . import views

paginator = PageNumberPagination()
paginator.page_size = settings.REST_FRAMEWORK.get("PAGE_SIZE", 10)

@api_view(["GET"])
def index(request):
    if request.method == "GET":
        return Response({
            "supplier-detail": resolve(reverse("api:supplier-detail", args=[0])).route,
            "supplier-entrynotes": resolve(reverse("api:supplier-entrynotes", args=[0])).route,
        })

######################## SUPPLIERS ########################

@api_view(["GET"])
@permission_required(["purchases.view_supplier"], raise_exception=True)
def supplier_list(request):
    if request.method == "GET":
        suppliers = Supplier.objects.all()
        serializer = SupplierListSerializer(suppliers, many=True)
        return Response(serializer.data)

@api_view(["GET"])
def supplier_detail(request, pk):

    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == "GET":
        if not (supplier.has_view_permission(request) or request.user.has_perms(["purchases.view_supplier", 
                                                                                 "quality.view_land", 
                                                                                 "quality.view_warehouse"])):
            return Response({"detail": "Permisos Insuficientes"}, status=status.HTTP_403_FORBIDDEN)
        serializer = SupplierDetailSerializer(supplier)
        return Response(serializer.data)


@api_view(["GET"])
def supplier_entrynotes(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == "GET":
        if not (supplier.has_view_permission(request) or request.user.has_perms(["purchases.view_supplier", 
                                                                                  "quality.view_entrynotes",])):
            return Response({"detail": "Permisos Insuficientes"}, status=status.HTTP_403_FORBIDDEN)
        entrynotes = EntryNote.objects.filter(supplier=supplier).order_by("-creation_date")
        entrynotes_paginated = paginator.paginate_queryset(entrynotes, request)
        serializer = EntryNoteListSerializer(entrynotes_paginated, many=True)
        return paginator.get_paginated_response(serializer.data)


######################## WAREHOUSE ########################

@api_view(["GET"])
@permission_required(["quality.view_warehouse"], raise_exception=True)
def warehouse_detail(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)

    if request.method == "GET":
        serializer = WarehouseDetailSerializer(warehouse)
        return Response(serializer.data)

######################## AGROFOODTYPE ########################

@api_view(["GET"])
@permission_required(["product.view_agrofoodtype"], raise_exception=True)
def agrofoodtype_detail(request, pk):
    agrofoodtype = get_object_or_404(AgrofoodType, pk=pk)

    if request.method == "GET":
        serializer = AgrofoodTypeDetailSerializer(agrofoodtype)
        return Response(serializer.data)

######################## CARRIERAGENT ########################

@api_view(["GET"])
@permission_required(["product.view_agrofoodtype"], raise_exception=True)
def carrier_detail(request, pk):
    carrier = get_object_or_404(CarrierAgent, pk=pk)

    if request.method == "GET":
        serializer = CarrierAgentDetailSerializer(carrier)
        return Response(serializer.data)

######################## ENTRY ########################
@api_view(["GET", "PUT"])
@permission_required(["purchases.change_entry"], raise_exception=True)
def entry_detail(request, pk):
    entry = get_object_or_404(Entry, pk=pk)

    if request.method == "GET":
        serializer = EntryDetailSerializer(entry)
        return Response(serializer.data)
    
    if request.method == "PUT":
        serializer = EntryDetailSerializer(entry, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"errors": serializer.errors} | EntryDetailSerializer(entry).data, status=status.HTTP_400_BAD_REQUEST)


######################## EXIT ########################
@api_view(["POST"])
@permission_required(["sales.add_exit"], raise_exception=True)
def exit_list(request):
    
    if request.method == "POST":
        serializer = ExitDetailSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["PUT"])
@permission_required(["sales.change_exit"], raise_exception=True)
def exit_detail(request, pk):
    exit = get_object_or_404(Exit, pk=pk)

    if request.method == "PUT":
        serializer = ExitDetailSerializer(exit, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"errors": serializer.errors} | ExitDetailSerializer(exit).data, status=status.HTTP_400_BAD_REQUEST)

