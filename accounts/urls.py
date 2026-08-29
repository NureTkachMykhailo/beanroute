from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("accounts/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/register/", views.register, name="register"),
    path("cabinet/", views.cabinet_overview, name="cabinet_overview"),
    path("cabinet/orders/", views.cabinet_orders, name="cabinet_orders"),
    path("cabinet/orders/<int:pk>/", views.cabinet_order_detail, name="cabinet_order_detail"),
    path("cabinet/wishlist/", views.cabinet_wishlist, name="cabinet_wishlist"),
    path("cabinet/reviews/", views.cabinet_reviews, name="cabinet_reviews"),
    path("cabinet/profile/", views.cabinet_profile, name="cabinet_profile"),
    path("cabinet/security/", views.cabinet_security, name="cabinet_security"),
    path("account/logs/", views.staff_logs, name="staff_logs"),
]
