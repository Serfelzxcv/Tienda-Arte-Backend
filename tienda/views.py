from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Producto, Carrito, CarritoItem, Orden, OrdenItem,Categoria  
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
class AgregarAlCarritoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        producto_id = request.data.get("producto_id")
        cantidad = int(request.data.get("cantidad", 1))

        producto = get_object_or_404(Producto, id=producto_id)
        if not producto.hay_stock(cantidad):
            return Response(
                {"error": "Stock insuficiente."},
                status=status.HTTP_400_BAD_REQUEST
            )

        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
        item, creado = CarritoItem.objects.get_or_create(carrito=carrito, producto=producto)
        item.cantidad += cantidad
        item.save()

        return Response({"mensaje": "Producto agregado al carrito."}, status=200)

# --- Eliminar item del carrito ---
class EliminarItemCarritoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, item_id):
        carrito = get_object_or_404(Carrito, usuario=request.user)
        item = get_object_or_404(CarritoItem, id=item_id, carrito=carrito)
        item.delete()
        return Response({"mensaje": "Item eliminado del carrito."}, status=204)

# --- Finalizar compra (crear orden) ---
class CrearOrdenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        carrito = get_object_or_404(Carrito, usuario=request.user)
        if not carrito.items.exists():
            return Response({"error": "Carrito vacío."}, status=400)

        orden = Orden.objects.create(usuario=request.user)
        total = 0

        for item in carrito.items.all():
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

            total += producto.precio * item.cantidad

        orden.total = total
        orden.save()
        carrito.items.all().delete()

        return Response({"mensaje": "Compra realizada con éxito."}, status=201)

# --- Ver historial de órdenes ---
class HistorialOrdenesView(generics.ListAPIView):
    serializer_class = OrdenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Orden.objects.filter(usuario=self.request.user).order_by('-creado')
