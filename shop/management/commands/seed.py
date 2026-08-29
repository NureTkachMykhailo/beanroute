import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import AuditEvent, RequestLog, UserProfile
from shop.models import (
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


class Command(BaseCommand):
    help = "Seed BeanRoute with demo data"

    def handle(self, *args, **options):
        SiteSettings.objects.get_or_create(pk=1)

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@beanroute.local", "admin12345")

        buyer, _ = User.objects.get_or_create(username="buyer", defaults={"email": "buyer@beanroute.local"})
        buyer.set_password("beanroute123")
        buyer.save()
        buyer_profile, _ = UserProfile.objects.get_or_create(user=buyer)
        buyer_profile.role = "buyer"
        buyer_profile.city = "Харків"
        buyer_profile.phone = "+380671234567"
        buyer_profile.save()

        staff, _ = User.objects.get_or_create(
            username="staff", defaults={"email": "staff@beanroute.local"}
        )
        staff.set_password("beanroute123")
        staff.is_staff = True
        staff.save()
        staff_profile, _ = UserProfile.objects.get_or_create(user=staff)
        staff_profile.role = "staff"
        staff_profile.save()

        categories_data = [
            ("Африка", "Яскрава кислотність, ягідні й квіткові ноти"),
            ("Латинська Америка", "Збалансовані сорти з горіховими й карамельними нотами"),
            ("Азія та Океанія", "Щільне тіло, землисті й пряні відтінки"),
            ("Бленди", "Купажі під різні способи заварювання"),
            ("Лімітовані партії", "Невеликі експериментальні лоти"),
        ]
        categories = {}
        for name, desc in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=name, defaults={"slug": slugify(name, allow_unicode=True), "description": desc}
            )
            categories[name] = cat

        products_data = [
            dict(
                name="Ефіопія Йоргачеффе", category="Африка", origin_country="Ефіопія",
                producer="Kochere Cooperative", process="washed", roast_level="light",
                altitude_m=1950, weight_g=250, price=420, stock=18,
                cupping_notes="Жасмин, бергамот, лимонна цедра",
                description="Мита ефіопська кава з високогірної кооперативи Кочере.",
                is_featured=True,
            ),
            dict(
                name="Кенія AA Ньєрі", category="Африка", origin_country="Кенія",
                producer="Tekangu Farmers", process="washed", roast_level="medium",
                altitude_m=1800, weight_g=250, price=460, stock=12,
                cupping_notes="Чорна смородина, помідор, вино",
                description="Класична кенійська AA з яскравою кислотністю.",
            ),
            dict(
                name="Колумбія Уїла", category="Латинська Америка", origin_country="Колумбія",
                producer="Finca El Paraiso", process="washed", roast_level="medium",
                altitude_m=1700, weight_g=250, price=380, stock=25,
                cupping_notes="Карамель, червоне яблуко, м'який горіх",
                description="Збалансований колумбійський лот із регіону Уїла.",
                is_featured=True,
            ),
            dict(
                name="Бразилія Серрадо", category="Латинська Америка", origin_country="Бразилія",
                producer="Fazenda Santa Ines", process="natural", roast_level="dark",
                altitude_m=1100, weight_g=250, price=320, stock=30,
                cupping_notes="Какао, лісовий горіх, коричневий цукор",
                description="Натуральна обробка, щільне тіло — добре в еспресо.",
            ),
            dict(
                name="Гватемала Антигуа", category="Латинська Америка", origin_country="Гватемала",
                producer="La Folie Estate", process="honey", roast_level="medium",
                altitude_m=1600, weight_g=250, price=410, stock=14,
                cupping_notes="Абрикос, мед, ваніль",
                description="Хані-обробка з вулканічних схилів Антигуа.",
            ),
            dict(
                name="Суматра Мандхелінг", category="Азія та Океанія", origin_country="Індонезія",
                producer="Lintong Farmers", process="natural", roast_level="dark",
                altitude_m=1300, weight_g=250, price=350, stock=20,
                cupping_notes="Кедр, чорний перець, темний шоколад",
                description="Землисто-пряний профіль, класика для темної обсмажки.",
            ),
            dict(
                name="Ранковий бленд", category="Бленди", origin_country="Купаж",
                producer="BeanRoute Blend Lab", process="washed", roast_level="medium",
                altitude_m=1400, weight_g=250, price=300, stock=40,
                cupping_notes="Збалансований, з горіховим фіналом",
                description="Щоденний бленд для фільтру й молочних напоїв.",
                is_featured=True,
            ),
            dict(
                name="Панама Гейша Лімітед", category="Лімітовані партії", origin_country="Панама",
                producer="Hacienda La Esmeralda", process="washed", roast_level="light",
                altitude_m=1900, weight_g=100, price=1250, stock=2,
                cupping_notes="Жасмин, персик, чорний чай",
                description="Легендарний сорт Гейша невеликою лімітованою партією.",
                is_featured=True,
            ),
        ]

        products = {}
        for data in products_data:
            cat = categories[data.pop("category")]
            slug = slugify(data["name"], allow_unicode=True)
            product, _ = Product.objects.get_or_create(
                slug=slug,
                defaults={**data, "category": cat, "lot_reference": f"BR-{random.randint(1000,9999)}"},
            )
            products[product.name] = product

        RoasteryService.objects.get_or_create(
            title="Підбір зерна", order=1,
            defaults={"description": "Допоможемо обрати зерно під ваш метод заварювання"},
        )
        RoasteryService.objects.get_or_create(
            title="Навчання бариста", order=2,
            defaults={"description": "Короткі курси для дому та кав'ярень"},
        )
        RoasteryService.objects.get_or_create(
            title="Оптові поставки", order=3,
            defaults={"description": "Регулярні партії для кав'ярень і офісів"},
        )

        Testimonial.objects.get_or_create(
            author_name="Олена, власниця кав'ярні",
            defaults={"quote": "Стабільна якість лот у лот, завжди свіжа дата обсмажки.", "order": 1},
        )
        Testimonial.objects.get_or_create(
            author_name="Дмитро, домашній бариста",
            defaults={"quote": "Паспорт кожного лота — це саме те, чого не вистачало іншим обсмажувальням.", "order": 2},
        )

        FAQItem.objects.get_or_create(
            question="Коли можна залишити відгук?",
            defaults={
                "answer": "Форма відгуку з'являється лише після підтвердженого замовлення цього лота.",
                "order": 1,
            },
        )
        FAQItem.objects.get_or_create(
            question="Як часто оновлюється каталог?",
            defaults={"answer": "Нові лоти з'являються щотижня, лімітовані партії — за наявності.", "order": 2},
        )
        FAQItem.objects.get_or_create(
            question="Чи можна замовити оптом?",
            defaults={"answer": "Так, для кав'ярень і офісів діють окремі умови — залиште заявку.", "order": 3},
        )

        now = timezone.now()
        order_specs = [
            ("Ефіопія Йоргачеффе", 2, "shipped", 40),
            ("Колумбія Уїла", 1, "paid", 25),
            ("Ранковий бленд", 3, "paid", 12),
            ("Панама Гейша Лімітед", 1, "pending", 2),
        ]
        last_order = None
        for name, qty, status, days_ago in order_specs:
            product = products[name]
            order = Order.objects.create(
                user=buyer, status=status, total=product.price * qty
            )
            Order.objects.filter(pk=order.pk).update(created_at=now - timedelta(days=days_ago))
            OrderItem.objects.create(order=order, product=product, quantity=qty, unit_price=product.price)
            last_order = order

        Review.objects.get_or_create(
            user=buyer, product=products["Ефіопія Йоргачеффе"],
            defaults={"rating": 5, "text": "Дуже яскравий, квітковий, саме те що люблю у light roast."},
        )
        Review.objects.get_or_create(
            user=buyer, product=products["Колумбія Уїла"],
            defaults={"rating": 4, "text": "Мʼякий і збалансований, гарно розкривається у фільтрі."},
        )

        WishlistItem.objects.get_or_create(user=buyer, product=products["Гватемала Антигуа"])
        WishlistItem.objects.get_or_create(user=buyer, product=products["Суматра Мандхелінг"])

        for event_type, days_ago in [("login", 6), ("order", 5), ("review", 4), ("login", 2), ("order", 1)]:
            ev = AuditEvent.objects.create(user=buyer, event_type=event_type)
            AuditEvent.objects.filter(pk=ev.pk).update(created_at=now - timedelta(days=days_ago))
        for event_type, days_ago in [("login", 3), ("logout", 3), ("login", 1)]:
            ev = AuditEvent.objects.create(user=staff, event_type=event_type)
            AuditEvent.objects.filter(pk=ev.pk).update(created_at=now - timedelta(days=days_ago))

        paths = ["/", "/catalog/", "/catalog/efiopiya-yorgacheffe/", "/cabinet/", "/api/products/"]
        methods_statuses = [("GET", 200), ("GET", 200), ("GET", 200), ("POST", 302), ("GET", 404)]
        for i in range(40):
            path = random.choice(paths)
            method, status_code = random.choice(methods_statuses)
            log = RequestLog.objects.create(
                user=random.choice([buyer, staff, None]),
                path=path,
                method=method,
                status_code=status_code,
                duration_ms=random.randint(15, 220),
                remote_addr="127.0.0.1",
            )
            RequestLog.objects.filter(pk=log.pk).update(
                created_at=now - timedelta(hours=random.randint(0, 96))
            )

        self.stdout.write(self.style.SUCCESS("Seed complete"))
