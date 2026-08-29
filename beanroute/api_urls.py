from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.api_views import me, register
from shop.api_views import CategoryViewSet, OrderViewSet, ProductViewSet, ReviewViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="api-categories")
router.register("products", ProductViewSet, basename="api-products")
router.register("orders", OrderViewSet, basename="api-orders")
router.register("reviews", ReviewViewSet, basename="api-reviews")

urlpatterns = [
    path("auth/register/", register, name="api_register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="api_login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="api_refresh"),
    path("auth/me/", me, name="api_me"),
] + router.urls
