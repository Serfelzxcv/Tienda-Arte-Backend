from django.db import models
from django.contrib.auth.models import User

# Perfil de los usuarios, con saldo
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    dinero = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Perfil de {self.user.username} - Saldo: {self.dinero}"

# Categorías fijas para los productos
class Categoria(models.TextChoices):
    CUADRO = 'CUADRO', 'Cuadro'
    ESCULTURA = 'ESCULTURA', 'Escultura'
    DISCO = 'DISCO', 'Disco'

# Modelo base de productos
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    categoria = models.CharField(max_length=20, choices=Categoria.choices)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} ({self.categoria})"

    def hay_stock(self, cantidad=1):
        return self.stock >= cantidad

class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Carrito de {self.usuario.username}"

class CarritoItem(models.Model):
    carrito = models.ForeignKey(
        Carrito, 
        on_delete=models.CASCADE,
        related_name='carrito_items'  # Cambia el related_name
    )
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    class Meta:
        verbose_name = 'Ítem de carrito'
        verbose_name_plural = 'Ítems de carrito'
    
class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

class Orden(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ordenes')
    creado = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Orden #{self.id} - {self.usuario.username}"

class OrdenItem(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def total(self):
        return self.precio_unitario * self.cantidad
