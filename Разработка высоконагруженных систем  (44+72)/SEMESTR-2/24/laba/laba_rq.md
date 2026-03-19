# Лабораторная работа: минимальный e-shop

## Цель 123

Довести интернет-магазин до рабочего варианта: каталог (уже есть) + **корзина** и **оформление заказа**. Ниже — анализ готового и пошаговая инструкция по тому, чего не хватает.

---

## Часть 1. Анализ: что уже сделано студентом

Перед добавлением корзины и заказа проверьте, что в проекте есть следующее.

### Модели (`shop/models.py`)

- **VideoCard** — товар: `name`, `price`, `description`, `created_at`.
- **Cart** — позиция в корзине: `product` (FK на VideoCard), `qty`, `created_at`. Поля для привязки к сессии пока нет — его добавляем в шагах ниже.
- **Order** — заказ: `total`, `created_at`.
- **OrderItem** — позиция заказа: `order`, `product_name`, `qty`, `price`.

### Views и URL (`shop/views.py`, `config/urls.py`)

- **Главная:** `home` → `/` — рендер полной страницы `shop/home.html`.
- **Компонент каталога:** `products_component` → `/components/products/` — фрагмент HTML со списком товаров (для HTMX).

### API (`shop/api.py`)

- GET `/api/products` — список товаров (JSON).
- GET `/api/products/{id}` — один товар (JSON).
- GET `/api/health` — `{"status": "ok"}`.

### Шаблоны

- `shop/templates/shop/home.html` — полная страница с HTMX, подгружающая список товаров.
- `shop/templates/shop/products_list.html` — цикл по товарам и подключение карточки.
- `shop/templates/shop/components/product_card.html` — карточка товара (название, цена, описание).

**Итог:** каталог и API работают; корзина и оформление заказа не реализованы. Переходим к ним.

---

## Справочно: сессии и HTMX

Перед реализацией корзины полезно понимать, как в проекте используются **сессии** (чтобы привязать корзину к браузеру) и **HTMX** (чтобы обновлять куски страницы без перезагрузки и без своего JavaScript).

### Сессии в Django

**Что такое сессия.** Сессия — это способ хранить данные по одному пользователю между запросами. У каждого браузера (после первого запроса к сайту) Django создаёт запись сессии и передаёт в браузер **cookie** с уникальным идентификатором — **session key** (ключ сессии). При следующих запросах браузер отправляет этот cookie, Django по нему находит сессию и даёт доступ к `request.session`.

**Где хранятся данные.** По умолчанию Django хранит сессии в БД (таблица `django_session`) или в файлах/кэше — в зависимости от `SESSION_ENGINE` в `settings.py`. В сессии можно сохранять, например, данные формы или флаг «корзина принадлежит этой сессии».

**Зачем сессия для корзины.** Мы не используем авторизацию: пользователь анонимный. Чтобы понимать, какая корзина чья, мы привязываем записи в модели `Cart` к **ключу сессии** (`session_key`). Один и тот же браузер всегда присылает один и тот же `session_key` — значит, все позиции корзины с этим ключом принадлежат одному «покупателю».

**Когда появляется session_key.** Ключ сессии создаётся при первом обращении к `request.session`. Иногда (например, при первом заходе на страницу) ключа ещё нет, пока сессия не сохранена. Поэтому в коде мы вызываем `request.session.create()`, если `request.session.session_key` пустой — так мы гарантируем, что ключ есть и его можно записать в `Cart.session_key`.

**Итог:** корзина привязана к сессии через поле `Cart.session_key`; при каждом запросе мы берём `_get_session_key(request)` и выбираем только позиции с этим ключом.

### HTMX в проекте

**Что такое HTMX.** HTMX — это небольшая JS-библиотека, которая по атрибутам в HTML отправляет запросы (GET, POST и др.) и **подставляет полученный ответ** в указанное место на странице. Писать свой JavaScript не нужно: достаточно разметки.

**Основные атрибуты (на примерах из проекта):**

- **`hx-get="URL"`** — по какому адресу делать GET-запрос.
- **`hx-post="URL"`** — по какому адресу отправить POST (например, форма удаления из корзины).
- **`hx-trigger="load"`** — когда выполнять запрос: `load` = при появлении элемента на странице (при загрузке).
- **`hx-swap="innerHTML"`** — куда подставить ответ: заменить внутреннее содержимое элемента (`innerHTML`).
- **`hx-target="CSS-селектор"`** — в какой элемент на странице подставить ответ (например, `#cart-content`). Если не указан, подстановка идёт в тот элемент, на котором висят атрибуты.

**Как это работает на главной.** В `home.html` есть блок с `hx-get="/components/products/"` и `hx-trigger="load"`. При загрузке страницы HTMX отправляет GET на `/components/products/`, сервер возвращает **фрагмент HTML** (список товаров). HTMX вставляет этот фрагмент внутрь блока — получается каталог без перезагрузки всей страницы и без отдельного JS.

**Как это работает при удалении из корзины.** В форме удаления стоят `hx-post="..."` и `hx-target="#cart-content"`. По нажатию кнопки HTMX отправляет POST на сервер, сервер удаляет позицию и возвращает **новый фрагмент списка корзины** (уже без удалённой строки). HTMX подставляет этот фрагмент в `#cart-content` — список на странице обновляется без перезагрузки.

**Заголовок HX-Request.** При запросе, инициированном HTMX, библиотека добавляет заголовок **`HX-Request: true`**. В view мы проверяем `request.headers.get("HX-Request")`: если запрос от HTMX, возвращаем только **HTML-фрагмент** (например, обновлённый список корзины), а не полную страницу. Так мы не дублируем логику «если HTMX — отдать фрагмент, иначе — редирект или полную страницу».

**Итог:** HTMX даёт «динамику» (подгрузка каталога, обновление корзины) за счёт разметки и ответов-фрагментов с сервера, без написания своего JS.

---

## Учебное задание: каталог через API

**Задание:** реализуйте страницу каталога, которая получает данные из `/api/products` и отображает их через JavaScript.

**Суть:** на главной странице каталог подгружается с сервера готовым HTML (view + HTMX). Тот же список товаров отдаёт и JSON API (`GET /api/products`). Задача — сделать отдельную страницу, где список товаров не приходит в HTML, а запрашивается по API и рисуется в браузере с помощью JavaScript (например, `fetch` + разбор JSON + вставка разметки в DOM).

**Что нужно сделать (если выполняете задание сами):**

1. Добавить маршрут и view, которые отдают одну HTML-страницу с контейнером под каталог (например, пустой `<div id="catalog-root">Загрузка…</div>`).
2. В этой странице написать скрипт, который при загрузке:
   - выполняет `fetch('/api/products')`;
   - проверяет ответ (`res.ok`), парсит JSON;
   - для каждого элемента массива строит HTML карточки товара (название, цена, описание) и вставляет в контейнер;
   - обрабатывает ошибки (сеть, неверный ответ) и пустой список.
3. Оформить карточки так же, как в основном каталоге (классы `.product`, `.name`, `.price`), чтобы внешний вид был единообразным.
4. На главной и на новой странице добавить ссылки для переключения: «Каталог (HTML с сервера)» и «Каталог (через API)».

**Что в итоге изучить:** разница между «данные в HTML с сервера» и «данные в JSON с API + отрисовка в браузере»; работа с `fetch`, Promise, DOM; экранирование вывода (`escapeHtml`), чтобы избежать XSS.

**Референс в проекте:** страница `/catalog-api/` и шаблон `shop/templates/shop/catalog_api.html` — пример готовой реализации этого задания. Сначала попробуйте сделать свою, затем сверьтесь с референсом.

---

## Часть 2. Что нужно добавить: корзина и оформление заказа

Нужно реализовать:

1. **Привязку корзины к сессии** — одна корзина на браузер (анонимный пользователь).
2. **Добавление в корзину** — кнопка «В корзину» в карточке товара, сохранение в БД по `session_key`.
3. **Страницу корзины** — просмотр позиций, итог, ссылка на оформление заказа.
4. **Удаление из корзины** — кнопка у позиции (при желании — с обновлением через HTMX).
5. **Оформление заказа** — страница подтверждения, создание `Order` и `OrderItem`, очистка корзины, страница «Заказ оформлен».

---

## Шаг 1. Привязка корзины к сессии

Корзина привязывается к браузеру через ключ сессии Django (см. раздел «Сессии в Django» выше).

1. В `shop/models.py` добавьте в модель **Cart** поле для сессии:

   ```python
   class Cart(models.Model):
       session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
       product = models.ForeignKey(VideoCard, on_delete=models.CASCADE)
       qty = models.IntegerField(default=1)
       created_at = models.DateTimeField(auto_now_add=True)
   ```

2. Создайте и примените миграцию:

   ```bash
   python manage.py makemigrations shop --name add_cart_session_key
   python manage.py migrate
   ```

**Проверка:** после миграции в таблице корзины есть столбец `session_key`.

---

## Шаг 2. Вспомогательная функция и view корзины

1. В `shop/views.py` добавьте импорты и функцию получения ключа сессии (сессия создаётся при первом обращении):

   ```python
   from django.shortcuts import render, redirect, get_object_or_404
   from django.views.decorators.http import require_POST
   from .models import VideoCard, Cart, Order, OrderItem

   def _get_session_key(request):
       if not request.session.session_key:
           request.session.create()
       return request.session.session_key
   ```

2. Добавьте view **компонента корзины** (фрагмент HTML для подстановки на страницу или по HTMX):

   ```python
   def cart_component(request):
       session_key = _get_session_key(request)
       items = Cart.objects.filter(session_key=session_key).select_related("product")
       total = sum((item.product.price * item.qty) for item in items)
       return render(
           request,
           "shop/components/cart_list.html",
           {"cart_items": items, "cart_total": total},
       )
   ```

3. Добавьте view **страницы корзины** (полная HTML-страница):

   ```python
   def cart_page(request):
       session_key = _get_session_key(request)
       items = Cart.objects.filter(session_key=session_key).select_related("product")
       total = sum((item.product.price * item.qty) for item in items)
       return render(
           request,
           "shop/cart.html",
           {"cart_items": items, "cart_total": total},
       )
   ```

---

## Шаг 3. Добавление товара в корзину

1. В `shop/views.py` добавьте view добавления в корзину (только POST):

   ```python
   @require_POST
   def cart_add(request, product_id):
       product = get_object_or_404(VideoCard, id=product_id)
       session_key = _get_session_key(request)
       cart_item, created = Cart.objects.get_or_create(
           session_key=session_key,
           product=product,
           defaults={"qty": 1},
       )
       if not created:
           cart_item.qty += 1
           cart_item.save()
       if request.headers.get("HX-Request"):
           return cart_component(request)
       return redirect(request.META.get("HTTP_REFERER") or "home")
   ```
   Проверка заголовка `HX-Request` нужна, чтобы при запросе от HTMX отдавать только фрагмент корзины, а при обычной отправке формы — делать редирект (см. раздел «HTMX в проекте»).

2. В `config/urls.py` зарегистрируйте маршруты и дайте имя главной (для `redirect("home")`):

   ```python
   path("", home, name="home"),
   path("components/cart/", cart_component),
   path("cart/", cart_page, name="cart_page"),
   path("cart/add/<int:product_id>/", cart_add, name="cart_add"),
   ```

3. В шаблоне карточки товара `shop/templates/shop/components/product_card.html` добавьте форму «В корзину»:

   ```html
   <form method="post" action="{% url 'cart_add' product.id %}">
     {% csrf_token %}
     <button type="submit">В корзину</button>
   </form>
   ```

4. На главной странице `shop/templates/shop/home.html` добавьте ссылку на корзину (например, перед блоком с товарами):

   ```html
   <p><a href="{% url 'cart_page' %}">Корзина</a></p>
   ```

**Проверка:** на главной нажать «В корзину» у товара, перейти по ссылке «Корзина» — должна открыться страница корзины с выбранным товаром.

---

## Шаг 4. Шаблон списка корзины и страница корзины

1. Создайте шаблон фрагмента корзины `shop/templates/shop/components/cart_list.html`:

   ```html
   {% if cart_items %}
     <ul class="cart-list">
       {% for item in cart_items %}
         <li class="cart-item">
           <span>{{ item.product.name }}</span>
           <span>{{ item.qty }} × {{ item.product.price|floatformat:0 }} ₽</span>
           <form method="post" action="{% url 'cart_remove' item.id %}" style="display:inline;"
                 hx-post="{% url 'cart_remove' item.id %}" hx-target="#cart-content" hx-swap="innerHTML">
             {% csrf_token %}
             <button type="submit" class="cart-remove">×</button>
           </form>
         </li>
       {% endfor %}
     </ul>
     <p class="cart-total">Итого: <strong>{{ cart_total|floatformat:0 }} ₽</strong></p>
     <a href="{% url 'checkout' %}">Оформить заказ</a>
   {% else %}
     <p class="cart-empty">Корзина пуста</p>
   {% endif %}
   ```

2. Создайте страницу корзины `shop/templates/shop/cart.html` (обёртка с контейнером `id="cart-content"` для HTMX при удалении — в этот блок HTMX подставит обновлённый фрагмент списка, см. раздел «HTMX в проекте»):

   ```html
   <!DOCTYPE html>
   <html lang="ru">
   <head>
     <meta charset="UTF-8">
     <title>Корзина</title>
     <script src="https://unpkg.com/htmx.org@2.0.3"></script>
     <style>
       .cart-item { display: flex; gap: 1rem; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #eee; }
       .cart-remove { background: #eee; border: none; cursor: pointer; width: 24px; height: 24px; border-radius: 4px; }
       .cart-total { margin-top: 1rem; font-size: 1.1rem; }
     </style>
   </head>
   <body>
     <h1>Корзина</h1>
     <a href="{% url 'home' %}">← На главную</a>
     <div class="cart-container" id="cart-content">
       {% include "shop/components/cart_list.html" %}
     </div>
   </body>
   </html>
   ```

**Проверка:** страница `/cart/` показывает позиции и итог; ссылка «Оформить заказ» ведёт на следующий шаг (её обработаем в шаге 6).

---

## Шаг 5. Удаление из корзины

1. В `shop/views.py` добавьте view удаления позиции (только POST, при HTMX-запросе возвращаем фрагмент корзины):

   ```python
   @require_POST
   def cart_remove(request, cart_item_id):
       session_key = _get_session_key(request)
       Cart.objects.filter(id=cart_item_id, session_key=session_key).delete()
       if request.headers.get("HX-Request"):
           return cart_component(request)
       return redirect("cart_page")
   ```

2. В `config/urls.py` добавьте маршрут:

   ```python
   path("cart/remove/<int:cart_item_id>/", cart_remove, name="cart_remove"),
   ```

В шаблоне `cart_list.html` форма удаления уже добавлена в шаге 4 (кнопка «×» с `hx-post` и `hx-target="#cart-content"`). HTMX по нажатию отправит POST, получит новый HTML-фрагмент списка корзины и подставит его в `#cart-content`, поэтому страница не перезагружается.

**Проверка:** на странице корзины нажать «×» у позиции — список обновится без перезагрузки страницы (HTMX) или с редиректом.

---

## Шаг 6. Оформление заказа

1. В `shop/views.py` добавьте view оформления заказа:
   - GET — показать страницу с составом корзины и кнопкой «Подтвердить заказ».
   - POST — создать `Order`, для каждой позиции корзины создать `OrderItem` (product_name, qty, price), очистить корзину текущей сессии, редирект на страницу успеха.

   ```python
   def checkout(request):
       session_key = _get_session_key(request)
       items = list(Cart.objects.filter(session_key=session_key).select_related("product"))
       if not items:
           return redirect("home")
       total = sum((item.product.price * item.qty) for item in items)
       if request.method == "POST":
           order = Order.objects.create(total=total)
           for item in items:
               OrderItem.objects.create(
                   order=order,
                   product_name=item.product.name,
                   qty=item.qty,
                   price=item.product.price,
               )
           Cart.objects.filter(session_key=session_key).delete()
           return redirect("checkout_success", order_id=order.id)
       return render(
           request,
           "shop/checkout.html",
           {"cart_items": items, "cart_total": total},
       )

   def checkout_success(request, order_id):
       order = get_object_or_404(Order, id=order_id)
       return render(request, "shop/checkout_success.html", {"order": order})
   ```

2. В `config/urls.py` добавьте маршруты:

   ```python
   path("checkout/", checkout, name="checkout"),
   path("checkout/success/<int:order_id>/", checkout_success, name="checkout_success"),
   ```

3. Создайте шаблон `shop/templates/shop/checkout.html`:
   - заголовок «Оформление заказа»;
   - ссылка «← В корзину» на `cart_page`;
   - список позиций (название, количество, цена);
   - итоговая сумма;
   - форма с `method="post"`, `{% csrf_token %}` и кнопкой «Подтвердить заказ».

4. Создайте шаблон `shop/templates/shop/checkout_success.html`:
   - заголовок «Заказ оформлен»;
   - номер заказа `{{ order.id }}`, сумма `{{ order.total }}`;
   - ссылка «Вернуться на главную» на `home`.

**Проверка:** положить товары в корзину → «Оформить заказ» → «Подтвердить заказ» → отображается страница успеха, корзина пуста, в БД есть заказ и позиции заказа.

---

## Шаг 7. Django 6 Tasks: уведомление о заказе (файл и email)

**Цель:** после оформления заказа ответ возвращается сразу, уведомление уходит в фоне через задачу (`@task`, `.enqueue()`, `on_commit`).

### 7.1. Настройка в settings.py

```python
TASKS = {"default": {"BACKEND": "django.tasks.backends.immediate.ImmediateBackend"}}
ORDER_NOTIFICATION_FILE = os.environ.get("ORDER_NOTIFICATION_FILE", str(BASE_DIR / "order_notifications.log"))
ORDER_NOTIFICATION_EMAIL = os.environ.get("ORDER_NOTIFICATION_EMAIL", "")
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@example.com")
```

### 7.2. Задача в shop/tasks.py

В задачу передаётся только **order_id** (int). Задача пишет данные заказа в файл и при наличии `ORDER_NOTIFICATION_EMAIL` отправляет письмо:

```python
from pathlib import Path
from django.conf import settings
from django.core.mail import send_mail
from django.tasks import task
from .models import Order

@task
def send_order_notification(order_id: int):
    order = Order.objects.filter(id=order_id).first()
    if not order:
        return
    items = order.orderitem_set.values_list("product_name", "qty", "price")
    text = f"Order #{order_id}, total {order.total}\n"
    text += "\n".join(f"  {name} x{qty} @ {price}" for name, qty, price in items)

    path = getattr(settings, "ORDER_NOTIFICATION_FILE", None)
    if path:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).open("a", encoding="utf-8").write(text + "\n")

    email = getattr(settings, "ORDER_NOTIFICATION_EMAIL", None)
    if email:
        send_mail(
            subject=f"Order #{order_id}",
            message=text,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", ""),
            recipient_list=[email],
            fail_silently=True,
        )
```

### 7.3. Вызов из checkout

В `checkout` при POST: обернуть создание заказа в `transaction.atomic()`, постановку задачи — в `transaction.on_commit()`:

```python
from functools import partial
from django.db import transaction
from .tasks import send_order_notification

# внутри if request.method == "POST":
with transaction.atomic():
    order = Order.objects.create(total=total)
    for item in items:
        OrderItem.objects.create(order=order, product_name=item.product.name, qty=item.qty, price=item.product.price)
    Cart.objects.filter(session_key=session_key).delete()
    transaction.on_commit(partial(send_order_notification.enqueue, order_id=order.id))
return redirect("checkout_success", order_id=order.id)
```

### 7.4. Проверка

1. Оформить заказ → редирект сразу.
2. В файле `order_notifications.log` — новая запись о заказе.
3. Если задан `ORDER_NOTIFICATION_EMAIL` — письмо в консоли (при `EMAIL_BACKEND=console`).

---

## Итоговая структура (корзина и заказ)

| URL | Назначение |
|-----|------------|
| `/` | Главная — каталог (HTML с сервера + HTMX). |
| `/catalog-api/` | Каталог через API — данные загружаются через JavaScript из `/api/products`. |
| `/cart/` | Страница корзины (полный HTML). |
| `/components/cart/` | Фрагмент HTML корзины (для HTMX при добавлении/удалении). |
| `POST /cart/add/<product_id>/` | Добавить товар в корзину. |
| `POST /cart/remove/<cart_item_id>/` | Удалить позицию из корзины. |
| `/checkout/` | Страница оформления заказа (GET — форма, POST — создание Order). |
| `/checkout/success/<order_id>/` | Страница «Заказ оформлен». |

### Файлы, которые добавляются или меняются

| Файл | Изменения |
|------|-----------|
| `shop/models.py` | Поле `Cart.session_key`. |
| `shop/views.py` | `home`, `catalog_via_api`, `_get_session_key`, `cart_component`, `cart_page`, `cart_add`, `cart_remove`, `checkout`, `checkout_success`; в `checkout` — `transaction.atomic()` и `on_commit(send_order_notification.enqueue)`. |
| `shop/tasks.py` | Задача `send_order_notification(order_id)` — запись в файл и email (Шаг 7). |
| `config/settings.py` | `TASKS`, `ORDER_NOTIFICATION_FILE`, `ORDER_NOTIFICATION_EMAIL`, `EMAIL_BACKEND`. |
| `config/urls.py` | Маршруты главной, каталога через API, корзины и checkout. |
| `shop/templates/shop/home.html` | Главная + ссылки «Каталог (HTML)», «Каталог (API)», «Корзина». |
| `shop/templates/shop/catalog_api.html` | Страница каталога через API (fetch + отрисовка в DOM). |
| `shop/templates/shop/components/product_card.html` | Форма «В корзину». |
| `shop/templates/shop/components/cart_list.html` | Новый шаблон — список позиций корзины. |
| `shop/templates/shop/cart.html` | Новый шаблон — страница корзины. |
| `shop/templates/shop/checkout.html` | Новый шаблон — оформление заказа. |
| `shop/templates/shop/checkout_success.html` | Новый шаблон — успешное оформление. |
| `shop/migrations/0002_...` | Миграция для `Cart.session_key`. |

После выполнения всех шагов у вас есть рабочий минимальный e-shop: каталог, корзина по сессии, оформление заказа с сохранением в Order и OrderItem, фоновая отправка уведомления о заказе через Django 6 Tasks (Шаг 7).
