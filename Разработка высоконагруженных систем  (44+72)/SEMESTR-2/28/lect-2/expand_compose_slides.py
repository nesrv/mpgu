# -*- coding: utf-8 -*-
"""Insert Docker Compose slides after slides 1-7; remove old single БАЗОВЫЙ block; fix overflow CSS."""
from pathlib import Path

HTML = Path(__file__).resolve().parent / "lect-arch-mq.html"
text = HTML.read_text(encoding="utf-8")

OLD_BLOCK = """<!-- ══ DOCKER COMPOSE: БАЗОВЫЙ ══ -->
<section class="compose-slide" data-background-color="#1a1a2e">
  <h2>Docker Compose: базовый старт RabbitMQ</h2>
  <p><em>Используется на слайдах 1–7 — «мастер-шаблон» для всех следующих примеров</em></p>
  <pre><code class="language-ini">services:
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"    # AMQP — клиентский протокол
      - "15672:15672"  # Management UI (браузер)
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest

  producer:
    build: .
    command: python producer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/

  consumer:
    build: .
    command: python consumer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/</code></pre>
  <p><em>Все примеры паттернов строятся на этом каркасе — меняются только <code>command</code> и число сервисов.</em></p>
</section>

"""

if OLD_BLOCK not in text:
    raise SystemExit("OLD_BLOCK not found — файл уже меняли вручную?")

text = text.replace(OLD_BLOCK, "", 1)

# Plain <code> without language-* — highlight.js не перекрашивает в «пустоту»
def compose_block(title, subtitle, yaml_body, bg="#1a1a2e"):
    return (
        f'<section class="compose-slide" data-background-color="{bg}">\n'
        f"  <h2>{title}</h2>\n"
        f"  <p><em>{subtitle}</em></p>\n"
        f'  <pre class="compose-pre"><code>{yaml_body}</code></pre>\n'
        f"</section>\n\n"
    )

C1 = compose_block(
    "Docker Compose · слайд 1",
    "Брокер + отдельные producer и consumer (как на схеме)",
    """services:
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
  producer:
    build: .
    command: python producer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  consumer:
    build: .
    command: python consumer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/""",
)

C2 = compose_block(
    "Docker Compose · слайд 2 (AMQP)",
    "Минимум: один процесс и публикует, и читает — exchange/очередь в коде",
    """services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  app:
    build: .
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/""",
    "#16213e",
)

C3 = compose_block(
    "Docker Compose · слайд 3 (vhost)",
    "Один контейнер rabbitmq; разные URI → разные vhost",
    """services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  shop-api:
    build: ./shop
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/shop
  billing-api:
    build: ./billing
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/billing""",
    "#2c3e50",
)

C4 = compose_block(
    "Docker Compose · слайд 4 (channel)",
    "Каналы — внутри процесса; в Compose один сервис = один TCP к брокеру",
    """services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  app:
    build: .
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
    # Внутри app: одно Connection, несколько Channel""",
    "#16213e",
)

C5a = compose_block(
    "Docker Compose · слайд 5 (путь сообщения)",
    "Producer → exchange → queue → consumer; declare в коде при старте",
    """services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  producer:
    build: .
    command: python producer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  consumer:
    build: .
    command: python consumer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/""",
    "#2c3e50",
)

C5b = compose_block(
    "Docker Compose · слайд 5 (несколько bindings)",
    "Три очереди и ключи — в коде order-сервиса и consumer'ов",
    """services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  orders:
    build: .
    command: python order_service.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  # billing_consumer, logistics_consumer, audit_consumer — отдельные services при желании""",
    "#2c3e50",
)

C6 = compose_block(
    "Docker Compose · слайд 6 (типы exchange)",
    "Тип exchange задаётся в приложении, не числом контейнеров",
    """services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  app:
    build: .
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/""",
    "#16213e",
)

C7 = compose_block(
    "Docker Compose · слайд 7 (очередь / prefetch)",
    "prefetch и ack — в коде consumer'а",
    """services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  worker:
    build: .
    command: python consumer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/""",
    "#2c3e50",
)

markers = [
    ("</section>\n\n<!-- ══ СЛАЙД 2: AMQP ══ -->", "<!-- ══ DOCKER COMPOSE: СЛАЙД 1 ══ -->\n" + C1),
    ("</section>\n\n<!-- ══ СЛАЙД 3: VHOST ══ -->", "<!-- ══ DOCKER COMPOSE: СЛАЙД 2 ══ -->\n" + C2),
    ("</section>\n\n<!-- ══ СЛАЙД 4: CONNECTION / CHANNEL ══ -->", "<!-- ══ DOCKER COMPOSE: СЛАЙД 3 ══ -->\n" + C3),
    ("</section>\n\n<!-- ══ СЛАЙД 5: ПУТЬ СООБЩЕНИЯ ══ -->", "<!-- ══ DOCKER COMPOSE: СЛАЙД 4 ══ -->\n" + C4),
]

for needle, insert in markers:
    if needle not in text:
        raise SystemExit(f"marker not found: {needle[:50]}...")
    text = text.replace(needle, insert + needle, 1)

# Slide 5: two sections — after first diagram, after second
m5a = "</section>\n\n<section data-background-color=\"#2c3e50\">\n  <h2>5. Один exchange — несколько bindings и очередей</h2>"
if m5a not in text:
    raise SystemExit("slide 5 part 2 marker not found")
text = text.replace(
    m5a,
    "<!-- ══ DOCKER COMPOSE: СЛАЙД 5a ══ -->\n" + C5a + m5a,
    1,
)

m5b = "</section>\n\n<!-- ══ СЛАЙД 6: ТИПЫ EXCHANGE ══ -->"
if m5b not in text:
    raise SystemExit("slide 5->6 marker not found")
text = text.replace(
    m5b,
    "<!-- ══ DOCKER COMPOSE: СЛАЙД 5b ══ -->\n" + C5b + m5b,
    1,
)

m67 = "</section>\n\n<!-- ══ СЛАЙД 7: ОЧЕРЕДЬ и UI ══ -->"
if m67 not in text:
    raise SystemExit("slide 6->7 marker not found")
text = text.replace(
    m67,
    "<!-- ══ DOCKER COMPOSE: СЛАЙД 6 ══ -->\n" + C6 + m67,
    1,
)

m78 = "</section>\n\n<!-- ══ СЛАЙД 8: ТЕМА И РЕЗУЛЬТАТ ══ -->"
if m78 not in text:
    raise SystemExit("slide 7->8 marker not found")
text = text.replace(
    m78,
    "<!-- ══ DOCKER COMPOSE: СЛАЙД 7 ══ -->\n" + C7 + m78,
    1,
)

# CSS: не вешать overflow:hidden на compose-slide через общий селектор section
old_css = "html, body, .reveal-viewport, .reveal, .reveal .slides, .reveal .slides section, .reveal .slide-background-content { overflow:hidden!important; scrollbar-width:none!important }"
new_css = (
    "html, body, .reveal-viewport, .reveal, .reveal .slides, .reveal .slide-background-content { overflow:hidden!important; scrollbar-width:none!important }\n"
    "    .reveal .slides section:not(.compose-slide) { overflow:hidden!important }"
)
if old_css not in text:
    raise SystemExit("CSS line 10 pattern not found")
text = text.replace(old_css, new_css, 1)

# Стили для plain-code блоков (без hljs)
needle_mermaid = "    .mermaid svg {"
if "pre.compose-pre" not in text:
    if needle_mermaid not in text:
        raise SystemExit(".mermaid svg CSS anchor not found")
    add = """
    .reveal .slides section.compose-slide pre.compose-pre {
      background: #272822 !important;
      border: 1px solid rgba(255,215,0,0.45) !important;
    }
    .reveal .slides section.compose-slide pre.compose-pre code {
      font-family: Consolas, "Ubuntu Mono", monospace !important;
      color: #f8f8f2 !important;
      background: transparent !important;
    }

"""
    text = text.replace(needle_mermaid, add + needle_mermaid, 1)

HTML.write_text(text, encoding="utf-8")
print("OK: compose slides expanded, CSS updated")
