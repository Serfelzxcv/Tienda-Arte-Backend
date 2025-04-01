from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import (
    RegistroUsuarioView,
    ProductoListCreateView,
    ProductoDetailView,
    CarritoView,
    AgregarAlCarritoView,
    EliminarItemCarritoView,
    CrearOrdenView,
    HistorialOrdenesView,
    ProductoCuadrosListView,
    ProductoEsculturasListView,
    ProductoDiscosListView
)

urlpatterns = [
    # Usuarios
    path('registro/', RegistroUsuarioView.as_view(), name='registro'),
    # Productos
    path('productos/', ProductoListCreateView.as_view(), name='productos'),
    path('productos/<int:pk>/', ProductoDetailView.as_view(), name='producto-detalle'),
    path('productos/cuadros/', ProductoCuadrosListView.as_view(), name='productos-cuadros'),
    path('productos/esculturas/', ProductoEsculturasListView.as_view(), name='productos-esculturas'),
    path('productos/discos/', ProductoDiscosListView.as_view(), name='productos-discos'),
    # Carrito
    path('carrito/', CarritoView.as_view(), name='carrito'),
    path('carrito/agregar/', AgregarAlCarritoView.as_view(), name='agregar-carrito'),
    path('carrito/item/<int:item_id>/', EliminarItemCarritoView.as_view(), name='eliminar-item'),

    # Órdenes
    path('ordenes/crear/', CrearOrdenView.as_view(), name='crear-orden'),
    path('ordenes/', HistorialOrdenesView.as_view(), name='ordenes'),
]
