# Презентация: HTMX и Django

*19 слайдов. В каждом блоке — явные примеры HTML / Django / JS / HTTP. Формат Markdown.*

---

## Слайд 1. HTMX — что это

**HTMX** — небольшая JS-библиотека (~14 KB), которая расширяет HTML **атрибутами**, а не фреймворком.

- Позволяет делать **частичные обновления страницы** без перезагрузки и без тяжёлого SPA.
- Идея: **гипермедиа** — сервер отдаёт **HTML-фрагменты**, браузер вставляет их в нужное место DOM.
- Слоган: *«HTML over the wire»* — вместо JSON + клиентский рендер.

**Зачем:** меньше JavaScript на клиенте, проще стек (Django, FastAPI, шаблоны).

**Два направления контракта:** (1) атрибуты в HTML → что и куда запрашивать; (2) **заголовки в ответе сервера** → редирект, события, target/swap.

**Пример подключения (один раз в base-шаблоне):**

```html
<script src="https://unpkg.com/htmx.org@2.0.4"></script>
```

---

## Слайд 2. Проблема, которую решает HTMX

| Подход | Плюсы | Минусы |
|--------|--------|--------|
| Форм + reload | Просто | Мерцает страница |
| SPA (React/Vue) | Богатый UI | Два «мира» (API + фронт) |
| **HTMX** | Частичные обновления, HTML с сервера | Не заменяет сложный клиентский UI |

**Сравнение «в лоб» — классический fetch vs HTMX:**

```js
// Без HTMX (каждый раз вручную)
fetch('/api/items').then(r => r.text()).then(html => {
  document.getElementById('list').innerHTML = html;
});
```

```html
<!-- С HTMX — то же поведение в разметке -->
<button hx-get="/items/partial/" hx-target="#list" hx-swap="innerHTML">Обновить</button>
<div id="list"></div>
```

---

## Слайд 3. Как это работает (модель)

1. Пользователь кликает / вводит текст / форма отправляется.
2. HTMX делает **HTTP-запрос** к URL из атрибута (+ заголовки `HX-*` с клиента).
3. Сервер возвращает **тело** (HTML) и при необходимости **заголовки ответа** `HX-*`.
4. HTMX **вставляет** фрагмент в DOM или выполняет действия по заголовкам.

**Что реально уходит в Network (упрощённо):**

```http
GET /items/partial/?q=phone HTTP/1.1
Host: example.com
HX-Request: true
HX-Target: #list
HX-Current-URL: https://example.com/shop/
```

**Тело ответа — просто HTML-фрагмент:**

```html
<ul><li>Товар A</li><li>Товар B</li></ul>
```

---

## Слайд 4. Атрибуты: запрос и куда вставить ответ

| Атрибут | Назначение |
|---------|------------|
| `hx-get` / `hx-post` / … | URL и метод |
| `hx-trigger` | Когда слать запрос |
| `hx-target` / `hx-swap` | Куда и как вставить |
| `hx-select` | Из ответа взять только узлы по селектору |
| `hx-include` / `hx-vals` | Доп. поля |

**Пример: поиск с задержкой (debounce):**

```html
<input type="search" name="q"
  hx-get="/search/"
  hx-trigger="keyup changed delay:400ms"
  hx-target="#results"
  hx-include="[name='category']"
  placeholder="Поиск…">
<select name="category" hx-get="/search/" hx-trigger="change" hx-target="#results">
  <option value="">Все</option>
</select>
<div id="results"></div>
```

**Пример `hx-vals` (доп. поля без input):**

```html
<button hx-post="/like/5/"
  hx-vals='{"source": "list"}'
  hx-target="#like-count-5">♥</button>
```

---

## Слайд 5. История, подтверждение, sync, файлы

| Атрибут | Назначение |
|---------|------------|
| `hx-push-url` | URL в историю после swap |
| `hx-confirm` / `hx-prompt` | Диалоги |
| `hx-params="none"` | Не слать поля формы |
| `hx-sync` | Очередь между элементами |

**Удаление с подтверждением:**

```html
<button hx-delete="/item/7/"
  hx-confirm="Удалить товар #7?"
  hx-target="closest tr"
  hx-swap="outerHTML swap:1s">Удалить</button>
```

**Два запроса не параллелятся (кнопка ждёт форму):**

```html
<form id="f" hx-post="/save">…</form>
<button hx-get="/preview/" hx-sync="#f:abort">Превью</button>
```

**Форма с файлом:**

```html
<form hx-post="/upload/" hx-encoding="multipart/form-data" enctype="multipart/form-data"
      hx-target="#status">
  {% csrf_token %}
  <input type="file" name="doc">
  <button type="submit">Загрузить</button>
</form>
<div id="status"></div>
```

---

## Слайд 6. Минимальный пример

**Клиент:**

```html
<button hx-get="/fragments/counter/"
        hx-target="#counter"
        hx-swap="innerHTML"
        hx-push-url="/stats">+1</button>
<div id="counter">0</div>
```

**Django view (фрагмент):**

```python
def counter_fragment(request):
    n = int(request.session.get("n", 0)) + 1
    request.session["n"] = n
    return HttpResponse(f"<span>{n}</span>")
```

**URL:** `path("fragments/counter/", counter_fragment)`.

---

## Слайд 7. Формы, валидация, multipart

**Клиент — форма целиком уходит в `#result`:**

```html
<form hx-post="/contact/" hx-target="#result" hx-swap="innerHTML">
  {% csrf_token %}
  <input name="email" type="email" required>
  <button type="submit">Отправить</button>
</form>
<div id="result"></div>
```

**Сервер — ошибка (тот же шаблон формы с ошибками):**

```python
def contact(request):
    if request.method == "POST":
        if not request.POST.get("email"):
            return render(request, "contact_form.html", {"error": "Нужен email"})
        return HttpResponse('<p class="ok">Отправлено</p>')
    return render(request, "contact_full.html")
```

**Успех с редиректом (см. слайд 9):** `response["HX-Redirect"] = "/thanks/"`.

---

## Слайд 8. Запрос с клиента: CSRF, Django, HX-Request

**Глобально подставить CSRF во все HTMX-запросы (в base после htmx):**

```html
<script>
  document.body.addEventListener('htmx:configRequest', function (evt) {
    evt.detail.headers['X-CSRFToken'] = '{{ csrf_token }}';
  });
</script>
```

**Во view — отдать partial или полную страницу:**

```python
def item_list(request):
    ctx = {"items": Item.objects.all()}
    if request.headers.get("HX-Request"):
        return render(request, "items/_rows.html", ctx)  # только &lt;tbody&gt;…
    return render(request, "items/list.html", ctx)
```

---

## Слайд 9. Ответ сервера: заголовки HX-*

| Заголовок | Действие |
|-----------|----------|
| `HX-Redirect` | Полный переход |
| `HX-Refresh` | Перезагрузка страницы |
| `HX-Trigger` | JSON событий на клиенте |

**Django — редирект после POST:**

```python
from django.http import HttpResponse

def create_order(request):
    # ... сохранение ...
    resp = HttpResponse(status=204)  # или пустой HTML
    resp["HX-Redirect"] = "/orders/"
    return resp
```

**Тост через событие:**

```python
resp = HttpResponse("<div>OK</div>")
resp["HX-Trigger"] = '{"toast": "Заказ создан"}'
return resp
```

```js
document.body.addEventListener('toast', (e) => alert(e.detail.value));
```

---

## Слайд 10. Ограничения и честные минусы

- Не заменяет тяжёлый клиентский state — там SPA.
- Много запросов — debounce, кэш, `hx-sync`.
- SEO: без JS ссылки должны работать.

**Пример `hx-select` (сервер отдал целую страницу — берём только блок):**

```html
<button hx-get="/page-with-layout/"
  hx-select="#main"
  hx-target="#main"
  hx-swap="outerHTML">Загрузить контент</button>
```

---

## Слайд 11. HTMX + Django / Ninja / FastAPI

| Стек | Пример |
|------|--------|
| Django | `render(request, "partial.html", ctx)` |
| FastAPI | `HTMLResponse(template.render({"request": request}))` |

**FastAPI (Jinja2) — фрагмент:**

```python
@app.get("/fragment/items", response_class=HTMLResponse)
def items_partial(request: Request):
    return templates.TemplateResponse("items_rows.html", {"request": request, "items": [...]})
```

---

## Слайд 12. Итоги и когда выбирать HTMX

**Выбирайте HTMX:** списки, формы, фильтры, пагинация, модалки; сильный бэкенд; MVP.

**SPA:** офлайн, очень сложный UI, большой клиентский state.

---

## Слайд 13. Out-of-band swap (oob)

**Страница:**

```html
<tbody id="cart-body">…</tbody>
<span id="cart-total">100 ₽</span>
```

**Ответ сервера одним куском:**

```html
<tr hx-swap-oob="innerHTML:#cart-body">
  <td>Товар</td><td>1</td>
</tr>
<!-- В HTMX 2 oob часто отдельными корневыми узлами; классический паттерн: -->
```

Классический oob (обновить бейдж и строку таблицы):

```html
<tr><td>Молоко</td><td>2</td></tr>
<div id="cart-badge" hx-swap-oob="true">3</div>
```

Если `hx-target` был `#cart-rows`, первая строка вставится туда; элемент с `id="cart-badge"` заменит одноимённый на странице.

---

## Слайд 14. Индикаторы и `hx-disabled-elt`

```html
<button hx-get="/slow/" hx-indicator="#spinner" hx-disabled-elt="this">
  Загрузить
</button>
<span id="spinner" class="htmx-indicator">⏳</span>
```

```css
.htmx-indicator { opacity: 0; transition: opacity 200ms; }
.htmx-request .htmx-indicator { opacity: 1; }
.htmx-request.htmx-indicator { opacity: 1; }
```

---

## Слайд 15. Расширения: SSE, WebSocket

```html
<script src="https://unpkg.com/htmx.org@2.0.4"></script>
<script src="https://unpkg.com/htmx-ext-sse@2.2.0/sse.js"></script>
<div hx-ext="sse" sse-connect="/events/stream" sse-swap="message">Ждём…</div>
```

Сервер отдаёт `text/event-stream` с `data: <div>обновление</div>`.

---

## Слайд 16. События HTMX и Hyperscript

```js
document.body.addEventListener('htmx:afterSwap', function (evt) {
  if (evt.detail.target.id === 'chat') {
    evt.detail.target.scrollTop = evt.detail.target.scrollHeight;
  }
});
```

---

## Слайд 17. Безопасность и тестирование

- Не доверять `HX-Target` для авторизации.
- Экранировать вывод (`{{ var }}` в Django).

**pytest (идея):**

```python
def test_partial(client):
    r = client.get("/items/", HTTP_HX_REQUEST="true")
    assert r.status_code == 200
    assert "<tbody" in r.content.decode() or "tr" in r.content.decode()
```

---

## Слайд 18. Шпаргалка: клиент ↔ сервер

**Клиент:** hx-get/post · target · swap · select · trigger · push-url · confirm · sync · multipart · boost · oob в ответе.

**Сервер:** HX-Redirect · Refresh · Trigger · Retarget · Reswap · Push-Url.

[htmx.org/reference](https://htmx.org/reference/)

---

## Слайд 19. Дорожная карта изучения

1. `hx-get` + partial с сервера  
2. Форма `hx-post` + ошибки HTML  
3. `HX-Redirect`  
4. `hx-select`  
5. oob  
6. `hx-sync` + индикатор  
7. SSE/WS, события, тесты  

---

*Конец презентации.*
