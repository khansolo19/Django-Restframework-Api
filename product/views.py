
from django.http import HttpResponse
from rest_framework.decorators import api_view, action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from .models import Product, Category, Like, Comment
from .serializers import ProductSerializer, CategorySerializer, CommentSerializer
from .permissions import IsCommentAuthor
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

class MyPaginationClass(PageNumberPagination):
    page_size = 8

    def get_paginated_response(self, data):
        return super().get_paginated_response(data)

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny, ]

    def get_permissions(self):
        """pereopredelim dannyi method"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permissions = [IsAdminUser]
        else:
            permissions = [AllowAny, ]
        return [permission() for permission in permissions]

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny, ]
    pagination_class = MyPaginationClass

    def get_serializer_context(self):
        return {'request': self.request}

    def get_permissions(self):
        """pereopredelim dannyi method"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permissions = [IsAdminUser]
        else:
            permissions = [AllowAny, ]
        return [permission() for permission in permissions]

    @action(detail=False, methods=['get'])
    def own(self, request, pk=None):
        queryset = self.get_queryset()
        queryset = queryset.filter(author=request.user)
        serializer = ProductSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def filter(self, request):
        queryset = self.queryset

        title = request.query_params.get('title')
        category = request.query_params.get('category')
        price = request.query_params.get('price')
        start_time = request.query_params.get('start_time')
        # available = request.query_params.get('available')

        if title == 'A-Z':
            queryset = self.get_queryset().order_by('title')
        elif title == 'Z-A':
            queryset = self.get_queryset().order_by('-title')
        elif category:
            queryset = queryset.filter(category=category)
        elif start_time == 'asc':
            queryset = self.get_queryset().order_by('start_time')
        elif start_time == 'desc':
            queryset = self.get_queryset().order_by('-start_time')
        elif price == 'asc':
            queryset = self.get_queryset().order_by('price')
        elif price == 'desc':
            queryset = self.get_queryset().order_by('-price')
        else:
            queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = self.action
        return context

    @action(detail=False, methods=['get'])  # action dostupny tol'ko v ViewSet / router builds path products/search/?q=blabla
    def search(self, request, pk=None):
        q = request.query_params.get('q')  # request.query_params = request.GET
        queryset = self.get_queryset()
        queryset = queryset.filter(Q(title__icontains=q) |
                                   Q(description__icontains=q))
        serializer = ProductSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@login_required
def toggle_like(request, id):
    product = Product.objects.get(id=id)
    if Like.objects.filter(user=request.user, product=product):
        Like.objects.get(user=request.user, product=product).delete()
    else:
        Like.objects.create(user=request.user, product=product)
    serializer = ProductSerializer(product)
    return Response(serializer.data)


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (AllowAny, )

    def get_permissions(self):
        """pereopredelim dannyi method"""
        if self.action == 'create':
            permissions = [IsAuthenticated, ]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permissions = [IsCommentAuthor, ]
        else:
            permissions = [AllowAny, ]
        return [permission() for permission in permissions]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

def write_db(request):
    import csv
    import os
    open('db.csv', 'w').close()
    products = Product.objects.all()
    with open('db.csv', 'w') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(('category', 'title', 'price', 'description', 'start_time', 'image', 'available'))
        for product in products:
            writer.writerow((product.category, product.title, product.price, product.description, product.start_time, product.image, product.available))
    with open('db.csv') as f:
        db = f.read()
    os.remove('db.csv')
    return HttpResponse(db, content_type='application/csv')