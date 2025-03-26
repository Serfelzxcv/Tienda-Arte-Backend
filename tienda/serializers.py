from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Producto, Carrito, CarritoItem, Orden, OrdenItem

# Usuario (registro)
class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        Carrito.objects.create(usuario=user)
        return user

# Producto
class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'


# Ítem del carrito
class CarritoItemSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all(), source='producto', write_only=True
    )

    class Meta:
        model = CarritoItem
        fields = ['id', 'producto', 'producto_id', 'cantidad', 'total']


# Carrito completo
class CarritoSerializer(serializers.ModelSerializer):
    items = CarritoItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Carrito
        fields = ['id', 'usuario', 'creado', 'items', 'total']

    def get_total(self, obj):
        return obj.total()


# OrdenItem
class OrdenItemSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)

    class Meta:
        model = OrdenItem
        fields = ['producto', 'cantidad', 'precio_unitario', 'total']


# Orden completa
class OrdenSerializer(serializers.ModelSerializer):
    items = OrdenItemSerializer(many=True, read_only=True)

    class Meta:
        model = Orden
        fields = ['id', 'usuario', 'creado', 'total', 'items']


