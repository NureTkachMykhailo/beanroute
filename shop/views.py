from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import AuditEvent

from .forms import ReviewForm
from .models import Category, FAQItem, Order, OrderItem, Product, Review, RoasteryService, Testimonial, WishlistItem


def landing(request):
    products = Product.objects.filter(is_active=True)
    stats = {
        "lots": products.count(),
        "categories": Category.objects.count(),
        "orders": Order.objects.exclude(status="cancelled").count(),
        "avg_rating": round(Review.objects.aggregate(a=Avg("rating"))["a"] or 0, 1),
    }
    featured = products.filter(is_featured=True).select_related("category")[:4]
    services = RoasteryService.objects.all()
    testimonials = Testimonial.objects.all()
    faqs = FAQItem.objects.all()
    return render(
        request,
        "shop/landing.html",
        {
            "stats": stats,
            "featured": featured,
            "services": services,
            "testimonials": testimonials,
            "faqs": faqs,
        },
    )


def catalog(request):
    products = Product.objects.select_related("category").filter(is_active=True)

    q = request.GET.get("q", "").strip()
    if q:
        products = products.filter(name__icontains=q) | products.filter(origin_country__icontains=q)

    category_slug = request.GET.get("category", "").strip()
    if category_slug:
        products = products.filter(category__slug=category_slug)

    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")
    if price_min:
        products = products.filter(price__gte=Decimal(price_min))
    if price_max:
        products = products.filter(price__lte=Decimal(price_max))

    sort_by = request.GET.get("sort", "-created_at")
    if sort_by in ["price", "-price", "-created_at", "name"]:
        products = products.order_by(sort_by)

    paginator = Paginator(products.distinct(), 6)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "shop/catalog.html",
        {
            "page_obj": page_obj,
            "categories": Category.objects.all(),
            "q": q,
            "category_slug": category_slug,
            "price_min": price_min or "",
            "price_max": price_max or "",
            "sort_by": sort_by,
            "result_count": products.count(),
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug)
    reviews = product.reviews.select_related("user").order_by("-created_at")
    similar = (
        Product.objects.filter(category=product.category, is_active=True)
        .exclude(pk=product.pk)
        .select_related("category")[:3]
    )

    has_purchased = False
    already_reviewed = False
    in_wishlist = False
    if request.user.is_authenticated:
        has_purchased = OrderItem.objects.filter(
            order__user=request.user, product=product
        ).exclude(order__status="cancelled").exists()
        already_reviewed = Review.objects.filter(user=request.user, product=product).exists()
        in_wishlist = WishlistItem.objects.filter(user=request.user, product=product).exists()

    review_form = ReviewForm()

    return render(
        request,
        "shop/product_detail.html",
        {
            "product": product,
            "reviews": reviews,
            "similar": similar,
            "has_purchased": has_purchased,
            "already_reviewed": already_reviewed,
            "in_wishlist": in_wishlist,
            "review_form": review_form,
        },
    )


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.delete()
        AuditEvent.objects.create(user=request.user, event_type="wishlist", meta=f"removed {product.name}")
    else:
        AuditEvent.objects.create(user=request.user, event_type="wishlist", meta=f"added {product.name}")
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"in_wishlist": created})
    return redirect("product_detail", slug=product.slug)


@login_required
def create_order(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1) or 1)
        if quantity < 1 or product.stock < quantity:
            messages.error(request, "Недостатньо залишку для цієї кількості.")
            return redirect("product_detail", slug=product.slug)

        order = Order.objects.create(user=request.user, total=product.price * quantity)
        OrderItem.objects.create(order=order, product=product, quantity=quantity, unit_price=product.price)
        product.stock -= quantity
        product.save(update_fields=["stock"])
        AuditEvent.objects.create(user=request.user, event_type="order", meta=f"order #{order.id}")
        messages.success(request, f"Замовлення №{order.id} створено.")
    return redirect("product_detail", slug=product.slug)


@login_required
def create_review(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    has_purchased = OrderItem.objects.filter(
        order__user=request.user, product=product
    ).exclude(order__status="cancelled").exists()

    if not has_purchased:
        messages.error(request, "Відгук можна залишити лише після покупки цього лота.")
        return redirect("product_detail", slug=product.slug)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            Review.objects.update_or_create(
                user=request.user,
                product=product,
                defaults={"rating": form.cleaned_data["rating"], "text": form.cleaned_data["text"]},
            )
            AuditEvent.objects.create(user=request.user, event_type="review", meta=f"review on {product.name}")
            messages.success(request, "Дякуємо за відгук!")
    return redirect("product_detail", slug=product.slug)
