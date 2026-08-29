from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import OrderItem


class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class HasPurchasedProduct(BasePermission):
    message = "Відгук можна залишити лише після покупки цього лота."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        product_id = request.data.get("product") or view.kwargs.get("product_id")
        if not product_id:
            return True
        return OrderItem.objects.filter(
            order__user=request.user, product_id=product_id
        ).exclude(order__status="cancelled").exists()


class IsOwnerOrStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, "user", None)
        return bool(request.user.is_staff or owner == request.user)
