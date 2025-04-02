from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Producto, Carrito, CarritoItem, Orden, OrdenItem,Categoria,Profile
from .serializers import (
    ProductoSerializer,
    CarritoSerializer,
    CarritoItemSerializer,
    OrdenSerializer,
    RegistroSerializer
)
from django.shortcuts import get_object_or_404
from django.db import transaction

# --- Registro de usuario ---
class RegistroUsuarioView(generics.CreateAPIView):
    serializer_class = RegistroSerializer
    permission_classes = [permissions.AllowAny]

# --- CRUD de productos ---
class ProductoListCreateView(generics.ListCreateAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ProductoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ProductoCuadrosListView(generics.ListAPIView):
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Producto.objects.filter(categoria=Categoria.CUADRO)

class ProductoEsculturasListView(generics.ListAPIView):
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return Producto.objects.filter(categoria=Categoria.ESCULTURA)

class ProductoDiscosListView(generics.ListAPIView):
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return Producto.objects.filter(categoria=Categoria.DISCO)

# --- Ver carrito del usuario ---
class CarritoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        carrito = get_object_or_404(Carrito, usuario=request.user)
        serializer = CarritoSerializer(carrito)
        return Response(serializer.data)

# --- Agregar producto al carrito ---

class CrearOrdenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:
            carrito = get_object_or_404(Carrito, usuario=request.user)
            profile = get_object_or_404(Profile, user=request.user)

            if profile is None:
                return Response({"error": "Profile no recibido."}, status=400)

            if not carrito.carrito_items.exists():
                return Response({"error": "Carrito vacío."}, status=400)

            total = sum(item.producto.precio * item.cantidad for item in carrito.carrito_items.all())

            if profile.dinero < total:
                return Response({"error": "Saldo insuficiente."}, status=400)

            orden = Orden.objects.create(usuario=request.user, total=total)

            for item in carrito.carrito_items.all():
                producto = item.producto
                if not producto.hay_stock(item.cantidad):
                    return Response(
                        {"error": f"Stock insuficiente para {producto.nombre}."},
                        status=400
                    )

                producto.stock -= item.cantidad
                producto.save()

                OrdenItem.objects.create(
                    orden=orden,
                    producto=producto,
                    cantidad=item.cantidad,
                    precio_unitario=producto.precio
                )

            # Descontar el saldo del usuario
            profile.dinero -= total
            profile.save()

            carrito.carrito_items.all().delete()

            return Response({"mensaje": "Compra realizada con éxito.", "orden_id": orden.id}, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

# --- Ver historial de órdenes ---
class HistorialOrdenesView(generics.ListAPIView):
    serializer_class = OrdenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Orden.objects.filter(usuario=self.request.user).order_by('-creado')
    
# views.py

def obtener_carrito(request):
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    serializer = CarritoSerializer(carrito)
    return Response(serializer.data)