from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("catalog/", views.catalog, name="catalog"),
    path("catalog/<str:slug>/", views.product_detail, name="product_detail"),
    path("wishlist/toggle/<int:product_id>/", views.toggle_wishlist, name="toggle_wishlist"),
    path("orders/create/<int:product_id>/", views.create_order, name="create_order"),
    path("reviews/create/<int:product_id>/", views.create_review, name="create_review"),
]
