# BeanRoute

Інтернет-магазин мікро-обсмажувальні спешелті кави — лабораторна робота №4 з дисципліни ВМПтФ. Django 6 + DRF + SimpleJWT + PostgreSQL, Docker Compose.

## Стек
- Django, Django REST Framework, djangorestframework-simplejwt
- PostgreSQL 15 (у Docker), SQLite для локальної розробки без Docker
- Gunicorn + WhiteNoise
- Server-side SVG-графіки (без сторонніх бібліотек/CDN)

Демо: `buyer` / `beanroute123`, `staff` / `beanroute123`, `admin` / `admin12345`.

## Рівні
- **1 (схема БД)** — `Category`, `Product`, `WishlistItem`, `Order`, `OrderItem`, `Review`, `SiteSettings`, `RoasteryService`, `Testimonial`, `FAQItem`, `UserProfile`, `RequestLog`, `AuditEvent`. `CheckConstraint`/`UniqueConstraint`, `PROTECT` на категорію й товар у позиції замовлення.
- **2 (ORM CRUD і REST API)** — DRF ViewSet-и `/api/categories/`, `/api/products/`, `/api/orders/`, `/api/reviews/`; вкладені `items` при створенні замовлення, ціна рахується на сервері.
- **3 (оптимізація запитів)** — індекси на ключових полях, `select_related`/`prefetch_related` у viewsets і кабінеті.
- **4 (безпека)** — `IsStaffOrReadOnly`, власник-або-staff для замовлень, `HasPurchasedProduct` для відгуків, `login_required` кабінет, staff-only `/account/logs/`.

## Функціональність
- Сесія (`/accounts/login/`, `/accounts/register/`) і JWT (`/api/auth/login/`, `/register/`, `/refresh/`, `/me/`)
- Вітрина з hero, агрегатами й FAQ; каталог із пошуком/фільтром/сортуванням і пагінацією
- Картка лота: паспорт характеристик, замовлення з перевіркою залишку, обране, відгук лише після покупки
- Кабінет покупця: огляд із SVG-графіками витрат і категорій, історія замовлень, обране, відгуки, профіль, безпека
- Staff-моніторинг `/account/logs/`: `RequestLog` + `AuditEvent`, фільтри, пагінація

## Запуск

```bash
docker compose up --build
# вітрина:  http://127.0.0.1:8000/
# API:      http://127.0.0.1:8000/api/
# admin:    http://127.0.0.1:8000/admin/
```

Або локально без Docker (SQLite):

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```
