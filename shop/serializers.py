from rest_framework import serializers

from .models import Category, Order, OrderItem, Product, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.name")
    rating_avg = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "category", "category_name", "origin_country",
            "roast_level", "process", "altitude_m", "weight_g", "price", "stock",
            "is_featured", "rating_avg", "created_at",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "unit_price"]
        read_only_fields = ["unit_price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "status", "total", "created_at", "items"]
        read_only_fields = ["status", "total"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        user = self.context["request"].user
        order = Order.objects.create(user=user, total=0)
        total = 0
        for item in items_data:
            product = item["product"]
            quantity = item.get("quantity", 1)
            if product.stock < quantity:
                order.delete()
                raise serializers.ValidationError(f"Недостатньо залишку для {product.name}")
            unit_price = product.price
            OrderItem.objects.create(order=order, product=product, quantity=quantity, unit_price=unit_price)
            product.stock -= quantity
            product.save(update_fields=["stock"])
            total += unit_price * quantity
        order.total = total
        order.save(update_fields=["total"])
        return order


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Review
        fields = ["id", "product", "username", "rating", "text", "created_at"]
        read_only_fields = ["username"]
