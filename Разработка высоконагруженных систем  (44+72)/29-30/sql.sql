-- Пользователи
-- Хранит информацию о пользователях мессенджера
-- username - уникальное имя пользователя
-- profile - настройки профиля (тема, уведомления, язык) в формате JSONB
CREATE TABLE users (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,  
    profile JSONB DEFAULT '{
        "theme": "light",
        "notifications": true,
        "language": "ru"
    }'
);

-- Сообщения канала
-- Хранит сообщения, опубликованные в информационном канале мессенджера
-- author_id - ссылка на пользователя-автора сообщения
-- title - заголовок сообщения (опционально)
-- content - текст сообщения
-- metadata - дополнительные данные (теги, время чтения, закрепление) в формате JSONB
-- stats - статистика сообщения (просмотры, лайки, комментарии) в формате JSONB
CREATE TABLE messages (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    author_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{
        "tags": [],
        "reading_time": 0,
        "is_pinned": false
    }',
    stats JSONB DEFAULT '{
        "views_count": 0,
        "likes_count": 0,
        "comments_count": 0
    }',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Комментарии к сообщениям
-- Хранит комментарии пользователей к сообщениям канала
-- message_id - ссылка на сообщение, к которому относится комментарий
-- author_id - ссылка на пользователя-автора комментария
-- parent_comment_id - ссылка на родительский комментарий (для вложенных комментариев)
-- content - текст комментария
-- metadata - дополнительные данные (редактирование, упоминания) в формате JSONB
-- reactions - реакции на комментарий в формате JSONB
CREATE TABLE comments (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    message_id INTEGER REFERENCES messages(id) ON DELETE CASCADE,
    author_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    parent_comment_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{
        "is_edited": false,
        "mentions": []
    }',
    reactions JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Наполнение таблиц тестовыми данными

-- Пользователи
INSERT INTO users (username, profile) VALUES
('alex_dev', '{"theme": "dark", "notifications": true, "language": "ru"}'),
('maria_tech', '{"theme": "light", "notifications": true, "language": "ru"}'),
('dmitry_coder', '{"theme": "dark", "notifications": false, "language": "ru"}'),
('anna_design', '{"theme": "light", "notifications": true, "language": "ru"}'),
('max_startup', '{"theme": "dark", "notifications": true, "language": "ru"}'),
('sofia_ai', '{"theme": "light", "notifications": true, "language": "ru"}'),
('ivan_web', '{"theme": "dark", "notifications": false, "language": "ru"}'),
('elena_mobile', '{"theme": "light", "notifications": true, "language": "ru"}');

-- Сообщения канала
INSERT INTO messages (author_id, title, content, metadata, stats, created_at) VALUES
(1, 'Как начать карьеру в IT без опыта', 
'Привет! Многие спрашивают, как попасть в IT без опыта. Вот несколько советов:
1. Выберите направление (веб, мобильная разработка, data science)
2. Пройдите онлайн-курсы или bootcamp
3. Создайте портфолио с реальными проектами
4. Участвуйте в open source проектах
5. Не бойтесь junior позиций - это старт!

Что думаете? Поделитесь своим опытом в комментариях!',
'{"tags": ["карьера", "IT", "советы"], "reading_time": 3, "is_pinned": true}',
'{"views_count": 1247, "likes_count": 89, "comments_count": 23}',
NOW() - INTERVAL '5 days'),

(2, 'Топ-5 инструментов для разработчиков в 2026',
'Обновил список инструментов, которые реально экономят время в 2026. Полезно как для тех, кто только начинает, так и для работающих программистов:

1. Cursor / GitHub Copilot X / Claude Sonnet - продвинутые AI-ассистенты с контекстом всего проекта
2. Warp / Tabby - современные терминалы с AI-подсказками
3. Postman / Insomnia - тестирование API с поддержкой GraphQL
4. Figma Dev Mode - интеграция дизайна и разработки
5. Linear / Jira - управление задачами с AI-планированием

Какие инструменты используете в работе? Что добавили бы в список?',
'{"tags": ["инструменты", "разработка", "продуктивность"], "reading_time": 2, "is_pinned": false}',
'{"views_count": 892, "likes_count": 67, "comments_count": 15}',
NOW() - INTERVAL '3 days'),

(3, 'GraphQL vs REST: что выбрать?',
'Частый вопрос на собеседованиях. Вот основные отличия:

REST:
- Простой и понятный
- Кэширование на уровне HTTP
- Множественные запросы для связанных данных

GraphQL:
- Один запрос для всех данных
- Типизация из коробки
- Гибкость в запросах

Для стартапов GraphQL часто удобнее, для больших систем - REST. А что используете вы?',
'{"tags": ["GraphQL", "REST", "API"], "reading_time": 4, "is_pinned": false}',
'{"views_count": 1563, "likes_count": 112, "comments_count": 34}',
NOW() - INTERVAL '2 days'),

(4, 'Как правильно составить резюме для IT',
'Работаю в HR IT-компании и вижу много ошибок. Вот что важно:

✅ Конкретные технологии и стек
✅ Реальные проекты с ссылками
✅ Метрики и достижения (увеличил производительность на 30%)
✅ GitHub профиль с кодом
❌ Не пишите "ответственный" и "коммуникабельный" без примеров

Есть вопросы по резюме? Пишите!',
'{"tags": ["резюме", "карьера", "советы"], "reading_time": 3, "is_pinned": false}',
'{"views_count": 2105, "likes_count": 145, "comments_count": 41}',
NOW() - INTERVAL '1 day'),

(5, 'Стартап или корпорация: где лучше работать?',
'Опыт работы и там, и там. Плюсы и минусы:

Стартап:
+ Быстрый рост, больше ответственности
+ Видишь результат своей работы
- Нестабильность, меньше структуры

Корпорация:
+ Стабильность, процессы, обучение
+ Больше ресурсов
- Медленнее продвижение, меньше влияния

Где работаете? Что выбираете?',
'{"tags": ["карьера", "стартап", "работа"], "reading_time": 3, "is_pinned": false}',
'{"views_count": 987, "likes_count": 78, "comments_count": 28}',
NOW() - INTERVAL '4 days'),

(6, 'ИИ в разработке: помощник или замена?',
'ChatGPT, Copilot, Claude - все используют. Но заменят ли они разработчиков?

Мое мнение: ИИ - отличный помощник, но не замена. Он:
- Помогает писать шаблонный код
- Объясняет сложные концепции
- Предлагает решения

Но не может:
- Принимать архитектурные решения
- Понимать бизнес-логику
- Работать с legacy кодом

Что думаете?',
'{"tags": ["AI", "разработка", "будущее"], "reading_time": 4, "is_pinned": true}',
'{"views_count": 1876, "likes_count": 134, "comments_count": 52}',
NOW() - INTERVAL '6 hours');

-- Комментарии к сообщениям
INSERT INTO comments (message_id, author_id, content, metadata, reactions, created_at) VALUES
(1, 2, 'Отличный пост! Добавлю: не забывайте про networking. Многие находят работу через знакомых в IT.', 
'{"is_edited": false, "mentions": []}', '{"like": 12, "love": 2}', NOW() - INTERVAL '5 days' + INTERVAL '2 hours'),

(1, 3, 'Согласен! Я начал с бесплатных курсов на YouTube, потом сделал несколько проектов и через 6 месяцев нашел первую работу.', 
'{"is_edited": false, "mentions": []}', '{"like": 8}', NOW() - INTERVAL '5 days' + INTERVAL '4 hours'),

(1, 4, 'А какие курсы посоветуете? Смотрю на Stepik и Coursera, но не знаю с чего начать.', 
'{"is_edited": false, "mentions": []}', '{"like": 3}', NOW() - INTERVAL '5 days' + INTERVAL '6 hours'),

(2, 1, 'Еще добавлю VS Code с расширениями - это must have для любого разработчика!', 
'{"is_edited": false, "mentions": []}', '{"like": 15, "love": 1}', NOW() - INTERVAL '3 days' + INTERVAL '1 hour'),

(2, 5, 'Linear действительно крутой! Перешли на него месяц назад, команда довольна.', 
'{"is_edited": false, "mentions": []}', '{"like": 5}', NOW() - INTERVAL '3 days' + INTERVAL '3 hours'),

(3, 2, 'Мы используем GraphQL в проекте, очень удобно! Особенно для мобильных приложений, где важна экономия трафика.', 
'{"is_edited": false, "mentions": []}', '{"like": 9, "love": 1}', NOW() - INTERVAL '2 days' + INTERVAL '1 hour'),

(3, 6, 'А как насчет производительности? Слышал, что GraphQL может быть медленнее из-за сложных запросов.', 
'{"is_edited": false, "mentions": []}', '{"like": 4}', NOW() - INTERVAL '2 days' + INTERVAL '5 hours'),

(3, 1, 'Зависит от реализации. С правильным кэшированием и DataLoader GraphQL работает отлично!', 
'{"is_edited": false, "mentions": []}', '{"like": 7}', NOW() - INTERVAL '2 days' + INTERVAL '7 hours'),

(4, 3, 'Спасибо за советы! Обновил резюме, добавил метрики. Надеюсь, поможет на собеседованиях.', 
'{"is_edited": false, "mentions": []}', '{"like": 11}', NOW() - INTERVAL '1 day' + INTERVAL '2 hours'),

(4, 5, 'А сколько проектов лучше указать? У меня их много, но боюсь перегрузить резюме.', 
'{"is_edited": false, "mentions": []}', '{"like": 2}', NOW() - INTERVAL '1 day' + INTERVAL '4 hours'),

(4, 4, 'Лучше 3-5 самых сильных проектов с подробным описанием, чем 10 без деталей. Качество важнее количества!', 
'{"is_edited": false, "mentions": []}', '{"like": 8}', NOW() - INTERVAL '1 day' + INTERVAL '6 hours'),

(5, 6, 'Работаю в стартапе уже год. Сложно, но очень интересно! Каждый день новые задачи.', 
'{"is_edited": false, "mentions": []}', '{"like": 6, "love": 1}', NOW() - INTERVAL '4 days' + INTERVAL '3 hours'),

(5, 2, 'Я в корпорации. Стабильно, но иногда скучно. Думаю перейти в стартап для опыта.', 
'{"is_edited": false, "mentions": []}', '{"like": 4}', NOW() - INTERVAL '4 days' + INTERVAL '5 hours'),

(6, 1, 'ИИ помогает мне писать тесты и документацию. Экономит кучу времени!', 
'{"is_edited": false, "mentions": []}', '{"like": 10}', NOW() - INTERVAL '6 hours' + INTERVAL '30 minutes'),

(6, 3, 'Боюсь, что через 5-10 лет junior позиций станет меньше. ИИ будет делать простые задачи.', 
'{"is_edited": false, "mentions": []}', '{"like": 3}', NOW() - INTERVAL '6 hours' + INTERVAL '1 hour'),

(6, 5, 'Не думаю, что стоит бояться. Технологии меняются, но разработчики всегда будут нужны. Просто задачи станут другими.', 
'{"is_edited": false, "mentions": []}', '{"like": 12, "love": 2}', NOW() - INTERVAL '6 hours' + INTERVAL '2 hours');

-- Вложенные комментарии (ответы на комментарии)
INSERT INTO comments (message_id, author_id, parent_comment_id, content, metadata, reactions, created_at) VALUES
(1, 1, 3, 'Рекомендую начать с бесплатных курсов на freeCodeCamp или The Odin Project. Потом можно перейти на платные, если понравится.', 
'{"is_edited": false, "mentions": []}', '{"like": 5}', NOW() - INTERVAL '5 days' + INTERVAL '8 hours'),

(3, 2, 7, 'Да, это правда. Но с правильной настройкой кэширования и ограничениями на глубину запросов можно решить эту проблему.', 
'{"is_edited": false, "mentions": []}', '{"like": 3}', NOW() - INTERVAL '2 days' + INTERVAL '9 hours'),

(4, 1, 10, 'Согласен! И не забывайте про адаптацию резюме под каждую вакансию. Это повышает шансы.', 
'{"is_edited": false, "mentions": []}', '{"like": 4}', NOW() - INTERVAL '1 day' + INTERVAL '8 hours');


