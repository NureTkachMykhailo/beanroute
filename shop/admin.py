from django.contrib import admin

from .models import (
    Category,
    FAQItem,
    Order,
    OrderItem,
    Product,
    Review,
    RoasteryService,
    SiteSettings,
    Testimonial,
    WishlistItem,
)

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(WishlistItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(SiteSettings)
admin.site.register(RoasteryService)
admin.site.register(Testimonial)
admin.site.register(FAQItem)
