"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter
from product.views import CommentViewSet, ProductViewSet, toggle_like, CategoryViewSet

schema_view = get_schema_view(
    openapi.Info(
        title='FULLTSACK',
        default_version='v1',
        description='Nurkamila is CRUSH',
    ),
    public = True
)
router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('category', CategoryViewSet)
router.register('comments', CommentViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('account/', include('account.urls')),
    path('export/', include('product.urls')),
    path('', include(router.urls)),
    path('products/<int:id>/toggle_like/', toggle_like),
    path('export/', include('product.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
