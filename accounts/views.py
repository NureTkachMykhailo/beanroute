from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import update_session_auth_hash
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from datetime import timedelta

from shop.models import Order, OrderItem, Review, WishlistItem

from .charts import bar_chart_svg, donut_chart_svg
from .forms import ProfileForm, RegisterForm
from .models import AuditEvent, RequestLog


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            AuditEvent.objects.create(user=user, event_type="register")
            login(request, user)
            return redirect("landing")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def cabinet_overview(request):
    orders = Order.objects.filter(user=request.user).exclude(status="cancelled")
    total_spent = orders.aggregate(s=Sum("total"))["s"] or 0
    wishlist_count = WishlistItem.objects.filter(user=request.user).count()
    avg_rating_given = Review.objects.filter(user=request.user).aggregate(a=Avg("rating"))["a"] or 0

    since = timezone.now() - timedelta(days=90)
    monthly = (
        orders.filter(created_at__gte=since)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("total"))
        .order_by("month")
    )
    spending_points = [(row["month"].strftime("%m.%y"), float(row["total"])) for row in monthly] or [("—", 0)]

    by_category = (
        OrderItem.objects.filter(order__user=request.user)
        .exclude(order__status="cancelled")
        .values("product__category__name")
        .annotate(n=Count("id"))
        .order_by("-n")
    )
    category_points = [(row["product__category__name"] or "—", row["n"]) for row in by_category] or [("—", 1)]

    last_order = orders.order_by("-created_at").first()
    recent_events = AuditEvent.objects.filter(user=request.user)[:8]

    return render(
        request,
        "accounts/cabinet_overview.html",
        {
            "orders_count": orders.count(),
            "total_spent": total_spent,
            "wishlist_count": wishlist_count,
            "avg_rating_given": round(avg_rating_given, 1),
            "spending_chart": bar_chart_svg(spending_points),
            "category_chart": donut_chart_svg(category_points),
            "last_order": last_order,
            "recent_events": recent_events,
            "active": "overview",
        },
    )


@login_required
def cabinet_order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"), pk=pk
    )
    if order.user != request.user and not request.user.is_staff:
        messages.error(request, "Це замовлення вам не належить.")
        return redirect("cabinet_orders")
    recent_events = AuditEvent.objects.filter(user=order.user)[:8]
    return render(
        request, "accounts/cabinet_order_detail.html", {"order": order, "recent_events": recent_events, "active": "orders"}
    )


@login_required
def cabinet_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items__product")
    return render(request, "accounts/cabinet_orders.html", {"orders": orders, "active": "orders"})


@login_required
def cabinet_wishlist(request):
    items = WishlistItem.objects.filter(user=request.user).select_related("product", "product__category")
    return render(request, "accounts/cabinet_wishlist.html", {"items": items, "active": "wishlist"})


@login_required
def cabinet_reviews(request):
    reviews = Review.objects.filter(user=request.user).select_related("product")
    return render(request, "accounts/cabinet_reviews.html", {"reviews": reviews, "active": "reviews"})


@login_required
def cabinet_profile(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            AuditEvent.objects.create(user=request.user, event_type="profile")
            messages.success(request, "Профіль оновлено.")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "accounts/cabinet_profile.html", {"form": form, "active": "profile"})


@login_required
def cabinet_security(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            AuditEvent.objects.create(user=request.user, event_type="profile", meta="password changed")
            messages.success(request, "Пароль змінено.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "accounts/cabinet_security.html", {"form": form, "active": "security"})


@user_passes_test(lambda u: u.is_staff, login_url="landing")
def staff_logs(request):
    logs = RequestLog.objects.select_related("user").all()

    username = request.GET.get("user", "").strip()
    if username:
        logs = logs.filter(user__username__icontains=username)

    status = request.GET.get("status", "").strip()
    if status:
        logs = logs.filter(status_code__gte=int(status), status_code__lt=int(status) + 100)

    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    if date_from:
        logs = logs.filter(created_at__date__gte=date_from)
    if date_to:
        logs = logs.filter(created_at__date__lte=date_to)

    stats = logs.aggregate(volume=Count("id"), avg_ms=Avg("duration_ms"))

    paginator = Paginator(logs, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    audit_recent = AuditEvent.objects.filter(event_type__in=["login", "logout"]).select_related("user")[:6]

    return render(
        request,
        "accounts/staff_logs.html",
        {
            "page_obj": page_obj,
            "stats": stats,
            "username": username,
            "status": status,
            "date_from": date_from or "",
            "date_to": date_to or "",
            "audit_recent": audit_recent,
            "active": "monitoring",
        },
    )
