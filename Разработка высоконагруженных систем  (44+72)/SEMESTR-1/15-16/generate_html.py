# Read the reference HTML to get styles
with open('../13-14/lab-postgresql-metodichka.html', 'r', encoding='utf-8') as f:
    ref_html = f.read()

# Extract styles section
style_start = ref_html.find('<style media="print">')
style_end = ref_html.find('</style>', ref_html.rfind('</style>')) + 8
styles = ref_html[style_start:style_end]

html_parts = []

# Part 1: Header
html_parts.append('''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Практика: Redis как брокер сообщений</title>
''')

html_parts.append(styles)

html_parts.append('''</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔴 Практическая работа</h1>
            <h2>Redis как брокер сообщений и буфер для PostgreSQL</h2>
            <p>Решение проблем высокой конкурентной нагрузки</p>
        </div>

        <div class="student-info">
            <div class="form-group">
                <label for="student-name">ФИО студента:</label>
                <input type="text" id="student-name" placeholder="Иванов Иван Иванович">
            </div>
            <div class="form-group">
                <label for="group">Группа:</label>
                <input type="text" id="group" placeholder="ИСТ-401">
            </div>
            <div class="form-group">
                <label for="date">Дата:</label>
                <input type="date" id="date">
            </div>
        </div>

        <div class="section">
            <h2>🎯 Цель занятия</h2>
            <p>Показать на практике:</p>
            <ul>
                <li>Как PostgreSQL <strong>не справляется с большим числом одновременных запросов на запись</strong></li>
                <li>Как это приводит к <strong>потере данных</strong>, <strong>таймаутам</strong> или <strong>зависанию</strong></li>
                <li>Как <strong>Redis как буфер/очередь</strong> решает проблему и обеспечивает надёжную обработку</li>
            </ul>
            
            <h3>🧰 Технологии</h3>
            <ul>
                <li><strong>FastAPI</strong> — веб-сервер</li>
                <li><strong>PostgreSQL</strong> — основная БД (в Docker)</li>
                <li><strong>Redis</strong> — буфер/очередь (в Docker)</li>
                <li><strong>Docker + Docker Compose</strong> — для развёртывания</li>
                <li><strong>Python-клиенты</strong>: asyncpg, aioredis</li>
                <li><strong>ab (Apache Bench)</strong> — для генерации нагрузки</li>
            </ul>
        </div>
''')

# Continue with more sections...
with open('lab-broker-redis-metodichka.html', 'w', encoding='utf-8') as f:
    f.write(''.join(html_parts))

print("HTML file created successfully!")
