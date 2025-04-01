from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from tienda.serializers import CustomTokenObtainPairSerializer

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Swagger
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi






schema_view = get_schema_view(
   openapi.Info(
      title="Tienda de Arte API",
      default_version='v1',
      description="API para tienda de arte (cuadros, esculturas, discos)",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tienda.urls')), 
    # JWT
    path('api/token/', TokenObtainPairView.as_view(serializer_class=CustomTokenObtainPairSerializer), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # App tienda
    path('api/', include('tienda.urls')),

    # Swagger & Redoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Archivos multimedia
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
