from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Producto, Carrito, CarritoItem, Orden, OrdenItem, Profile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Carrito, ItemCarrito

# Usuario (registro)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Agrega datos del usuario a la respuesta
        user = self.user
        data['user'] = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'dinero': user.profile.dinero  # Accede al saldo a través del Profile
        }
        return data
# serializers.py
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
        Profile.objects.create(user=user)  # Crear perfil con saldo 0
        return user
    
# Profile
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['dinero']
        read_only_fields = ['user']

# Producto
class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'


# Ítem del carrito
class CarritoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarritoItem
        fields = ['id', 'producto', 'cantidad']


# Carrito completo

class ItemCarritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCarrito
        fields = ['producto', 'cantidad']
        
class CarritoSerializer(serializers.ModelSerializer):
    items = CarritoItemSerializer(many=True, source='carrito_items')  # Usa el nuevo related_name

    class Meta:
        model = Carrito
        fields = ['id', 'usuario', 'items', 'creado', 'actualizado']

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


