from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.urls import reverse, resolve
from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer

from base.models import Agent
from packaging.utils import packaging_balance
from product.models import AgrofoodType
from purchases.models import Supplier, CarrierAgent, Entry, EntryNote
from quality.models import Warehouse
from sales.models import Exit


from .serializers import SupplierListSerializer, SupplierDetailSerializer, WarehouseDetailSerializer, AgrofoodTypeDetailSerializer, CarrierAgentDetailSerializer, EntryDetailSerializer, ExitDetailSerializer, EntryNoteListSerializer, PackagingBalanceSerializer

paginator = PageNumberPagination()
paginator.page_size = settings.REST_FRAMEWORK.get("PAGE_SIZE", 10)

######################## INDEX ########################

@api_view(["GET"])
def index(request):
    if request.method == "GET":
        return Response({
            "authorization": resolve(reverse("api:authentication-token")).route,
            "supplier-detail": resolve(reverse("api:supplier-detail", args=[0])).route,
            "supplier-entrynotes": resolve(reverse("api:supplier-entrynotes", args=[0])).route,
            "agent-packaging-balance": resolve(reverse("api:agent-packaging-balance", args=[0])).route,
        })

######################## TOKEN AUTHENTICATION ########################

@api_view(["POST"])
def authentication_token(request):
    """
    curl -X POST http://127.0.0.1:8000/api/auth-token/"}' "Content-Type: application/json" -d '{"username": "username", "password": "password"}'
    """
    if request.method == "POST":
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        response_data = {"token": token.key}
        if user.agent:
            response_data["supplier_id"] = user.agent.pk
        return Response(response_data)

######################## SUPPLIERS ########################

@api_view(["GET"])
@permission_classes([IsAdminUser])
@permission_required(["purchases.view_supplier"], raise_exception=True)
def supplier_list(request):
    if request.method == "GET":
        suppliers = Supplier.objects.all()
        serializer = SupplierListSerializer(suppliers, many=True)
        return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == "GET":
        if not (supplier.is_user_from(request) or request.user.has_perms(["purchases.view_supplier", 
                                                                                 "quality.view_land", 
                                                                                 "quality.view_warehouse"])):
            return Response({"detail": "Usted no tiene permiso para realizar esta acción"}, status=status.HTTP_403_FORBIDDEN)
        serializer = SupplierDetailSerializer(supplier)
        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def supplier_entrynotes(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == "GET":
        if not (supplier.is_user_from(request) or request.user.has_perms(["purchases.view_supplier", 
                                                                          "quality.view_entrynotes",])):
            return Response({"detail": "Usted no tiene permiso para realizar esta acción"}, status=status.HTTP_403_FORBIDDEN)
        entrynotes = EntryNote.objects.filter(supplier=supplier).order_by("-creation_date")
        entrynotes_paginated = paginator.paginate_queryset(entrynotes, request)
        serializer = EntryNoteListSerializer(entrynotes_paginated, many=True)
        return paginator.get_paginated_response(serializer.data)

######################## AGENT ########################

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def agent_packaging_balance(request, pk):
    agent = get_object_or_404(Agent, pk=pk)
    balance = packaging_balance(agent=agent) 

    if request.method == "GET":
        if not (agent.is_user_from(request) or request.user.has_perms(["packaging.view_transaction"])):
            return Response({"detail": "Usted no tiene permiso para realizar esta acción"}, status=status.HTTP_403_FORBIDDEN)
        serializer = PackagingBalanceSerializer(data=balance, many=True)
        serializer.is_valid()
        return Response(serializer.data)


######################## WAREHOUSE ########################

@api_view(["GET"])
@permission_classes([IsAdminUser])
@permission_required(["quality.view_warehouse"], raise_exception=True)
def warehouse_detail(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)

    if request.method == "GET":
        serializer = WarehouseDetailSerializer(warehouse)
        return Response(serializer.data)

######################## AGROFOODTYPE ########################

@api_view(["GET"])
@permission_classes([IsAdminUser])
@permission_required(["product.view_agrofoodtype"], raise_exception=True)
def agrofoodtype_detail(request, pk):
    agrofoodtype = get_object_or_404(AgrofoodType, pk=pk)

    if request.method == "GET":
        serializer = AgrofoodTypeDetailSerializer(agrofoodtype)
        return Response(serializer.data)

######################## CARRIERAGENT ########################

@api_view(["GET"])
@permission_classes([IsAdminUser])
@permission_required(["product.view_agrofoodtype"], raise_exception=True)
def carrier_detail(request, pk):
    carrier = get_object_or_404(CarrierAgent, pk=pk)

    if request.method == "GET":
        serializer = CarrierAgentDetailSerializer(carrier)
        return Response(serializer.data)

######################## ENTRY ########################
@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAdminUser])
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
@permission_classes([IsAdminUser])
@permission_required(["sales.change_exit"], raise_exception=True)
def exit_detail(request, pk):
    exit = get_object_or_404(Exit, pk=pk)

    if request.method == "PUT":
        serializer = ExitDetailSerializer(exit, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"errors": serializer.errors} | ExitDetailSerializer(exit).data, status=status.HTTP_400_BAD_REQUEST)

