from django.db.models import Prefetch
from rest_framework import viewsets

from .models import Category, Order, OrderItem, Product, Review
from .permissions import HasPurchasedProduct, IsOwnerOrStaff, IsStaffOrReadOnly
from .serializers import CategorySerializer, OrderSerializer, ProductSerializer, ReviewSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsStaffOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        return Product.objects.select_related("category").prefetch_related("reviews").filter(is_active=True)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsOwnerOrStaff]

    def get_queryset(self):
        qs = Order.objects.select_related("user").prefetch_related(
            Prefetch("items", queryset=OrderItem.objects.select_related("product"))
        )
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [HasPurchasedProduct, IsOwnerOrStaff]

    def get_queryset(self):
        return Review.objects.select_related("user", "product", "product__category")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
