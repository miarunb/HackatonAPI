from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework.decorators import api_view, action
from rest_framework.filters import OrderingFilter
from rest_framework import viewsets, mixins, status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .filters import ProductFilter
from .models import Product, Category, WishList, Review, Favorite, Cart
from .permissions import IsAuthorOrAdminPermission
from .serializers import (ProductListSerializer, ProductDetailsSerializer, CategorySerializer, ReviewSerializer,
                          FavoriteListSerializer, CartListSerializer)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductDetailsSerializer
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filterset_class = ProductFilter
    ordering_fields = ['name', 'price']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        elif self.action in ['create_review', 'like']:
            return [IsAuthenticated()]
        return []

    @action(detail=False, methods=['get'])
    def search(self, request, pk=None):
        q = request.query_params.get('q')
        queryset = self.get_queryset()
        queryset = queryset.filter(Q(name__icontains=q))
        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def create_review(self, request, pk):
        data = request.data.copy()
        data['product'] = pk
        serializer = ReviewSerializer(data=data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=201)


    @action(detail=True, methods=['post'])
    def like(self, request, pk):
        product = self.get_object()
        user = request.user
        like_obj, created = WishList.objects.get_or_create(product=product, user=user)
        if like_obj.is_liked:
            like_obj.is_liked = False
            like_obj.save
            return Response('disliked')
        else:
            like_obj.is_liked = True
            like_obj.save()
            return Response('liked')

    @action(detail=True, methods=['post'])
    def add_to_favorite(self, request, pk):
        product = self.get_object()
        user = request.user
        fav, created = Favorite.objects.get_or_create(product=product, user=user)
        if fav.favorite:
            fav.favorite = False
            fav.save
            return Response('Удален из избранных')
        else:
            fav.favorite = True
            fav.save()
            return Response('Добавлен в избранные')

    @action(detail=True, methods=['post'])
    def add_to_cart(self, request, pk):
        product = self.get_object()
        user = request.user
        in_cart, created = Cart.objects.get_or_create(product=product, user=user)
        if in_cart.to_cart:
            in_cart.to_cart = False
            in_cart.save
            return Response('Удален из корзины')
        else:
            in_cart.to_cart = True
            in_cart.save()
            return Response('Добавлен в корзину')

class ReviewViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthorOrAdminPermission()]


class Favorites(ListAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteListSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def  get_serializer_context(self):
        return {'request': self.request}


class CartView(ListAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartListSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def  get_serializer_context(self):
        return {'request': self.request}