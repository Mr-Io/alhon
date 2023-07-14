from rest_framework import serializers

from packaging.models import Packaging, Transaction
from product.models import AgrofoodType
from purchases.models import Supplier, CarrierAgent, Charge, Entry, EntryNote, Invoice
from quality.models import Land, Warehouse
from sales.models import Exit

#################### PACKAGING ####################
class PackagingTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Packaging
        fields = ["pk", "name"]

#################### AGROFOODTYPE ####################
class AgrofoodTypeListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="__str__")
    class Meta:
        model = AgrofoodType
        fields = ["pk", "name"]

class AgrofoodTypeDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="__str__")
    packaging = PackagingTypeListSerializer(read_only=True)
    class Meta:
        model = AgrofoodType
        fields = ["pk", "name", "packaging"]


#################### WAREHOUSE ####################
class WarehouseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ["pk", "name"]

class WarehouseDetailSerializer(serializers.ModelSerializer):
    agrofoodtypes = AgrofoodTypeListSerializer(many=True, read_only=True)
    class Meta:
        model = Warehouse
        fields = ["pk", "name", "agrofoodtypes"]

#################### CARRIERAGENT ####################
class CarrierAgentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarrierAgent
        fields = ["pk", "name", "carrier_price"]

class CarrierAgentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarrierAgent
        fields = ["pk", "name", "carrier_price"]


#################### CHARGE ####################
class ChargeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Charge
        fields = ["pk", "name"]

#################### SUPPLIER ####################
class SupplierListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ["pk", "name"]

class LandExpandSerializer(serializers.ModelSerializer):
    warehouse_set = WarehouseListSerializer(many=True, read_only=True)
    class Meta:
        model=Land
        fields = ["pk", "name", "warehouse_set"]

class SupplierDetailSerializer(serializers.ModelSerializer):
    land_set = LandExpandSerializer(many=True, read_only=True)
    carrier = CarrierAgentListSerializer(read_only=True)
    charge = ChargeListSerializer(read_only=True)
    class Meta:
        model = Supplier
        fields = ["pk", "name", "cif", "mobile", "carrier", "charge", "land_set"]

#################### TRANSACTION ####################
class TransactionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["pk", "packaging", "agent", "number"]

class TransactionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["pk"]

#################### ENTRY ####################
class EntryListSerializer(serializers.ModelSerializer):
    agrofood = serializers.CharField(source="agrofood.name", read_only=True)
    num_packages = serializers.IntegerField(source="packaging_transaction.number", read_only=True)
    class Meta:
        model = Entry
        fields= ["pk", "num_packages", "agrofood", "weight", "price"]


class EntryDetailSerializer(serializers.ModelSerializer):
    warehouse = WarehouseListSerializer(read_only=True)
    agrofood = AgrofoodTypeListSerializer(read_only=True)
    packaging_transaction = TransactionListSerializer(read_only=True)
    class Meta:
        model = Entry
        fields= ["pk", "price", "warehouse", "agrofood", "packaging_transaction"]


#################### ENTRYNOTE ####################
class EntryNoteDetailSerializer(serializers.ModelSerializer):
    carrier = CarrierAgentListSerializer(read_only=True)
    charge = ChargeListSerializer(read_only=True)
    class Meta:
        model = EntryNote
        fields= "__all__"

class EntryNoteListSerializer(serializers.ModelSerializer):
    carrier = serializers.CharField(source="carrier.name", allow_null=True)
    charge = serializers.CharField(source="charge.name")
    entry_set = EntryListSerializer(read_only=True, many=True)
    settlement = serializers.IntegerField(read_only=True, source="invoice.settlement.pk", allow_null=True)
    class Meta:
        model = EntryNote
        fields= ["pk", "tax_amount", "charge", "carrier", "registered", "invoice", "settlement", "creation_date", "entry_set",]


#################### EXIT ####################
class ExitDetailSerializer(serializers.ModelSerializer):
    packaging_transaction = TransactionDetailSerializer()
    class Meta:
        model = Exit
        fields= ["pk", "entry", "client", "weight", "price", "packaging_transaction"]
    
    def create(self, validated_data):
        if 'packaging_transaction' in validated_data:
            transaction_data = validated_data.pop('packaging_transaction')
            transaction = Transaction.objects.create(**transaction_data)
        else:
            transaction = None
        return Exit.objects.create(packaging_transaction = transaction, **validated_data)
        
