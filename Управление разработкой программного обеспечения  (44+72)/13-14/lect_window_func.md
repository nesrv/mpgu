# 🪟 Оконные, агрегатные и группирующие функции в PostgreSQL

---

## Слайд 1: Титульный

### 🪟 Оконные, агрегатные и группирующие функции в PostgreSQL

**Теория**  
**МПГУ, 4 курс, 2025**

---

## Слайд 2: Актуальность для OLTP и OLAP

### 🎯 Зачем нужны оконные функции?

**OLTP (Online Transaction Processing):**
- Ранжирование пользователей по активности
- Расчет накопительных сумм (баланс счета)
- Сравнение текущей и предыдущей транзакции

**OLAP (Online Analytical Processing):**
- Аналитика продаж по периодам
- Скользящие средние для трендов
- Ранжирование товаров по выручке

**Преимущества:**
- ✅ Один запрос вместо множества
- ✅ Не требуется GROUP BY
- ✅ Доступ к соседним строкам

---

## Слайд 3: Оконные функции — базовый синтаксис

### 📊 OVER() — окно по всей таблице

**Визуализация:**
```
Продажи:
┌────────┬────────┬────────┐
│ Товар  │ Сумма  │ Всего  │  ← OVER() считает по всем строкам
├────────┼────────┼────────┤
│ Яблоки │  100   │  600   │
│ Груши  │  150   │  600   │
│ Бананы │  200   │  600   │
│ Киви   │  150   │  600   │
└────────┴────────┴────────┘
```

**SQL:**
```sql
SELECT 
    product,
    amount,
    SUM(amount) OVER() as total  -- Сумма по всем строкам
FROM sales;
```

---

## Слайд 4: PARTITION BY — разделение на группы

### 🔀 OVER(PARTITION BY) — окно по группам

**Визуализация:**
```
Продажи по категориям:
┌──────────┬────────┬────────┬──────────────┐
│ Категория│ Товар  │ Сумма  │ Итог группы │
├──────────┼────────┼────────┼──────────────┤
│ Фрукты   │ Яблоки │  100   │    450       │ ← Группа 1
│ Фрукты   │ Груши  │  150   │    450       │
│ Фрукты   │ Бананы │  200   │    450       │
├──────────┼────────┼────────┼──────────────┤
│ Овощи    │ Морковь│   80   │    150       │ ← Группа 2
│ Овощи    │ Капуста│   70   │    150       │
└──────────┴────────┴────────┴──────────────┘
```

**SQL:**
```sql
SELECT 
    category,
    product,
    amount,
    SUM(amount) OVER(PARTITION BY category) as category_total
FROM sales;
```

---

## Слайд 5: Нарастающий итог (Running Total)

### 📈 Визуализация нарастающего итога

```
Продажи по дням:
┌──────┬────────┬─────────────┐
│ День │ Сумма  │ Накопленная │
├──────┼────────┼─────────────┤
│  1   │  100   │    100      │ ← 100
│  2   │  150   │    250      │ ← 100 + 150
│  3   │  200   │    450      │ ← 100 + 150 + 200
│  4   │  150   │    600      │ ← 100 + 150 + 200 + 150
└──────┴────────┴─────────────┘
```

**SQL:**
```sql
SELECT 
    day,
    amount,
    SUM(amount) OVER(ORDER BY day) as running_total
FROM daily_sales;
```

---

## Слайд 5.1: Нарастающий итог с группировкой

### 📊 PARTITION BY + ORDER BY

**SQL:**
```sql
SELECT 
    category,
    day,
    amount,
    SUM(amount) OVER(
        PARTITION BY category 
        ORDER BY day
    ) as category_running_total
FROM sales;
```

**Результат:**
```
┌───────────┬──────┬────────┬────────────────────────┐
│ category  │ day  │ amount │ category_running_total │
├───────────┼──────┼────────┼────────────────────────┤
│ Фрукты    │  1   │  100   │         100            │ ← Начало группы
│ Фрукты    │  2   │  150   │         250            │ ← 100 + 150
│ Фрукты    │  3   │  200   │         450            │ ← 100 + 150 + 200
├───────────┼──────┼────────┼────────────────────────┤
│ Овощи     │  1   │   80   │          80            │ ← Новая группа
│ Овощи     │  2   │   70   │         150            │ ← 80 + 70
│ Овощи     │  3   │   90   │         240            │ ← 80 + 70 + 90
└───────────┴──────┴────────┴────────────────────────┘
         ↑                           ↑
    Разделение              Накопление внутри
    на группы               каждой группы
```

**💡 Ключевое отличие:** PARTITION BY сбрасывает счетчик для каждой категории

---

## Слайд 6: Скользящая рамка (Window Frame)

### 🎯 ROWS BETWEEN — скользящее окно

**Визуализация скользящего среднего (3 дня):**
```
┌──────┬────────┬──────────────────┐
│ День │ Сумма  │ Среднее за 3 дня │
├──────┼────────┼──────────────────┤
│  1   │  100   │      100         │ ← только день 1
│  2   │  150   │      125         │ ← (100+150)/2
│  3   │  200   │      150         │ ← (100+150+200)/3
│  4   │  180   │      177         │ ← (150+200+180)/3
│  5   │  220   │      200         │ ← (200+180+220)/3
└──────┴────────┴──────────────────┘
         ↑↑↑
      Окно 3 дня
```

**Типы рамок:**
- `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW` — 3 строки (2 предыдущие + текущая)
- `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` — от начала до текущей
- `ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING` — предыдущая + текущая + следующая

---

## Слайд 7: Скользящее среднее за 3 дня

### 📊 Реализация на PostgreSQL

**SQL:**
```sql
SELECT 
    day,
    amount,
    AVG(amount) OVER(
        ORDER BY day
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as moving_avg_3days
FROM daily_sales;
```

**Результат:**
```
┌──────┬────────┬──────────────────┐
│ day  │ amount │ moving_avg_3days │
├──────┼────────┼──────────────────┤
│  1   │  100   │      100.00       │ ← (100)/1
│  2   │  150   │      125.00       │ ← (100+150)/2
│  3   │  200   │      150.00       │ ← (100+150+200)/3
│  4   │  180   │      176.67       │ ← (150+200+180)/3
│  5   │  220   │      200.00       │ ← (200+180+220)/3
│  6   │  190   │      196.67       │ ← (180+220+190)/3
└──────┴────────┴──────────────────┘
         ↑↑↑
      Окно 3 дня
```

**💡 Применение:** сглаживание трендов, анализ временных рядов

---

## Слайд 7.1: Сумма за последние 7 дней

### 📈 Анализ недельной выручки

**SQL:**
```sql
SELECT 
    date,
    revenue,
    SUM(revenue) OVER(
        ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as last_7days_revenue
FROM sales;
```

**Результат:**
```
┌────────────┬─────────┬───────────────────┐
│    date    │ revenue │ last_7days_revenue │
├────────────┼─────────┼───────────────────┤
│ 2025-01-01 │   100   │        100         │ ← 1 день
│ 2025-01-02 │   120   │        220         │ ← 2 дня
│ 2025-01-03 │   150   │        370         │ ← 3 дня
│ 2025-01-04 │   130   │        500         │
│ 2025-01-05 │   140   │        640         │
│ 2025-01-06 │   160   │        800         │
│ 2025-01-07 │   180   │        980         │ ← 7 дней
│ 2025-01-08 │   200   │       1080         │ ← убирается 01-01
│ 2025-01-09 │   190   │       1150         │ ← убирается 01-02
└────────────┴─────────┴───────────────────┘
                      ↑↑↑↑↑↑↑
                   Окно 7 дней
```

**💡 Применение:** мониторинг недельной выручки, KPI дашборды

---

## Слайд 8: LEAD() и LAG() — доступ к соседним строкам

### ⬅️➡️ Функции навигации

**LAG() — предыдущая строка:**
```sql
SELECT 
    date,
    price,
    LAG(price, 1) OVER(ORDER BY date) as prev_price,
    price - LAG(price, 1) OVER(ORDER BY date) as price_change
FROM stock_prices;
```

**Результат:**
```
┌────────────┬───────┬────────────┬──────────────┐
│    date    │ price │ prev_price │ price_change │
├────────────┼───────┼────────────┼──────────────┤
│ 2025-01-01 │  100  │    NULL    │     NULL     │
│ 2025-01-02 │  105  │    100     │      +5      │
│ 2025-01-03 │   98  │    105     │      -7      │
└────────────┴───────┴────────────┴──────────────┘
```

**LEAD() — следующая строка:**
```sql
SELECT 
    employee,
    salary,
    LEAD(salary, 1) OVER(ORDER BY salary DESC) as next_salary
FROM employees;
```

---

## Слайд 9: FIRST_VALUE() и LAST_VALUE()

### 🎯 Первое и последнее значение в окне

**FIRST_VALUE() — первое значение:**
```sql
SELECT 
    product,
    date,
    price,
    FIRST_VALUE(price) OVER(
        PARTITION BY product 
        ORDER BY date
    ) as initial_price
FROM product_prices;
```

**LAST_VALUE() — последнее значение:**
```sql
SELECT 
    product,
    date,
    price,
    LAST_VALUE(price) OVER(
        PARTITION BY product 
        ORDER BY date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as final_price
FROM product_prices;
```

**⚠️ Важно:** Для LAST_VALUE() нужно указать `UNBOUNDED FOLLOWING`, иначе будет текущая строка!

---

## Слайд 10: RANK(), DENSE_RANK(), ROW_NUMBER()

### 🏆 Функции ранжирования

**Сравнение функций:**
```sql
SELECT 
    student,
    score,
    ROW_NUMBER() OVER(ORDER BY score DESC) as row_num,
    RANK() OVER(ORDER BY score DESC) as rank,
    DENSE_RANK() OVER(ORDER BY score DESC) as dense_rank
FROM exam_results;
```

**Результат:**
```
┌─────────┬───────┬─────────┬──────┬────────────┐
│ student │ score │ row_num │ rank │ dense_rank │
├─────────┼───────┼─────────┼──────┼────────────┤
│ Иван    │  95   │    1    │  1   │     1      │
│ Петр    │  90   │    2    │  2   │     2      │
│ Мария   │  90   │    3    │  2   │     2      │ ← одинаковый балл
│ Анна    │  85   │    4    │  4   │     3      │ ← RANK пропускает 3
└─────────┴───────┴─────────┴──────┴────────────┘
```

**Различия:**
- `ROW_NUMBER()` — уникальный номер (1,2,3,4)
- `RANK()` — пропускает номера при равенстве (1,2,2,4)
- `DENSE_RANK()` — не пропускает номера (1,2,2,3)

---

## Слайд 11: NTILE() — разделение на группы

### 📊 Квартили и процентили

**Разделение на 4 квартиля:**
```sql
SELECT 
    customer,
    revenue,
    NTILE(4) OVER(ORDER BY revenue DESC) as quartile
FROM customer_revenue;
```

**Результат:**
```
┌──────────┬─────────┬──────────┐
│ customer │ revenue │ quartile │
├──────────┼─────────┼──────────┤
│ Client A │  10000  │    1     │ ← Топ 25%
│ Client B │   8000  │    1     │
│ Client C │   6000  │    2     │
│ Client D │   5000  │    2     │
│ Client E │   3000  │    3     │
│ Client F │   2000  │    3     │
│ Client G │   1000  │    4     │ ← Нижние 25%
│ Client H │    500  │    4     │
└──────────┴─────────┴──────────┘
```

**Применение:** ABC-анализ, сегментация клиентов

---

## Слайд 12: crosstab() — сводные таблицы

### 🔄 Преобразование строк в столбцы

**Установка расширения:**
```sql
CREATE EXTENSION IF NOT EXISTS tablefunc;
```

**Пример данных:**
```sql
-- Исходная таблица
SELECT * FROM sales;
┌─────────┬─────────┬────────┐
│ product │  month  │ amount │
├─────────┼─────────┼────────┤
│ Яблоки  │ Январь  │  100   │
│ Яблоки  │ Февраль │  150   │
│ Груши   │ Январь  │  200   │
│ Груши   │ Февраль │  180   │
└─────────┴─────────┴────────┘
```

**Сводная таблица:**
```sql
SELECT * FROM crosstab(
    'SELECT product, month, amount FROM sales ORDER BY 1,2',
    'SELECT DISTINCT month FROM sales ORDER BY 1'
) AS ct(product TEXT, january INT, february INT);
```

**Результат:**
```
┌─────────┬─────────┬──────────┐
│ product │ january │ february │
├─────────┼─────────┼──────────┤
│ Яблоки  │   100   │   150    │
│ Груши   │   200   │   180    │
└─────────┴─────────┴──────────┘
```

---

## Слайд 13: GROUPING SETS — множественная группировка

### 🎯 Несколько GROUP BY в одном запросе

**Без GROUPING SETS (3 запроса):**
```sql
SELECT category, NULL as region, SUM(amount) FROM sales GROUP BY category
UNION ALL
SELECT NULL, region, SUM(amount) FROM sales GROUP BY region
UNION ALL
SELECT NULL, NULL, SUM(amount) FROM sales;
```

**С GROUPING SETS (1 запрос):**
```sql
SELECT 
    category,
    region,
    SUM(amount) as total
FROM sales
GROUP BY GROUPING SETS (
    (category),        -- Группировка по категории
    (region),          -- Группировка по региону
    ()                 -- Общий итог
);
```

**Результат:**
```
┌──────────┬────────┬───────┐
│ category │ region │ total │
├──────────┼────────┼───────┤
│ Фрукты   │  NULL  │  450  │ ← По категории
│ Овощи    │  NULL  │  150  │
│  NULL    │ Москва │  300  │ ← По региону
│  NULL    │ СПб    │  300  │
│  NULL    │  NULL  │  600  │ ← Общий итог
└──────────┴────────┴───────┘
```

---

## Слайд 14: ROLLUP — иерархические итоги

### 📊 Промежуточные итоги по иерархии

**Синтаксис:**
```sql
SELECT 
    year,
    quarter,
    month,
    SUM(revenue) as total
FROM sales
GROUP BY ROLLUP(year, quarter, month);
```

**Результат:**
```
┌──────┬─────────┬───────┬────────┐
│ year │ quarter │ month │ total  │
├──────┼─────────┼───────┼────────┤
│ 2025 │   Q1    │  Jan  │  1000  │ ← Детализация
│ 2025 │   Q1    │  Feb  │  1200  │
│ 2025 │   Q1    │  NULL │  2200  │ ← Итог Q1
│ 2025 │   Q2    │  Apr  │  1500  │
│ 2025 │   Q2    │  NULL │  1500  │ ← Итог Q2
│ 2025 │   NULL  │  NULL │  3700  │ ← Итог 2025
│ NULL │   NULL  │  NULL │  3700  │ ← Общий итог
└──────┴─────────┴───────┴────────┘
```

**Применение:** финансовые отчеты, иерархические структуры

---

## Слайд 15: CUBE — все комбинации группировок

### 🎲 Многомерный анализ

**Синтаксис:**
```sql
SELECT 
    category,
    region,
    SUM(amount) as total
FROM sales
GROUP BY CUBE(category, region);
```

**Результат (все комбинации):**
```
┌──────────┬────────┬───────┐
│ category │ region │ total │
├──────────┼────────┼───────┤
│ Фрукты   │ Москва │  200  │ ← category + region
│ Фрукты   │ СПб    │  250  │
│ Фрукты   │  NULL  │  450  │ ← только category
│ Овощи    │ Москва │  100  │
│ Овощи    │ СПб    │   50  │
│ Овощи    │  NULL  │  150  │
│  NULL    │ Москва │  300  │ ← только region
│  NULL    │ СПб    │  300  │
│  NULL    │  NULL  │  600  │ ← общий итог
└──────────┴────────┴───────┘
```

**Сравнение:**
- `ROLLUP(a, b)` → (a,b), (a), ()
- `CUBE(a, b)` → (a,b), (a), (b), ()

---

## Слайд 16: Практические примеры

### 💼 Реальные задачи

**1. Топ-3 товара в каждой категории:**
```sql
SELECT * FROM (
    SELECT 
        category,
        product,
        revenue,
        RANK() OVER(PARTITION BY category ORDER BY revenue DESC) as rank
    FROM products
) t WHERE rank <= 3;
```

**2. Процент от общей суммы:**
```sql
SELECT 
    product,
    revenue,
    ROUND(100.0 * revenue / SUM(revenue) OVER(), 2) as percent
FROM sales;
```

**3. Сравнение с предыдущим периодом:**
```sql
SELECT 
    month,
    revenue,
    LAG(revenue) OVER(ORDER BY month) as prev_month,
    ROUND(100.0 * (revenue - LAG(revenue) OVER(ORDER BY month)) / 
          LAG(revenue) OVER(ORDER BY month), 2) as growth_percent
FROM monthly_sales;
```

---

## Слайд 17: Заключение

### 🎯 Ключевые выводы

**Оконные функции:**
- ✅ Мощный инструмент для аналитики
- ✅ Заменяют сложные подзапросы
- ✅ Повышают производительность

**Когда использовать:**
- Ранжирование и рейтинги
- Накопительные итоги
- Сравнение с предыдущими периодами
- Скользящие средние
- Многомерный анализ (CUBE, ROLLUP)

**Рекомендации:**
- Используйте индексы для ORDER BY
- Избегайте избыточных PARTITION BY
- Тестируйте производительность на больших данных

---

## Слайд 18: Полезные ссылки

### 📚 Документация и ресурсы

- [PostgreSQL Window Functions](https://www.postgresql.org/docs/current/tutorial-window.html)
- [PostgreSQL GROUPING SETS](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-GROUPING-SETS)
- [tablefunc Extension](https://www.postgresql.org/docs/current/tablefunc.html)

**Практика:**
- [SQL Window Functions Practice](https://www.windowfunctions.com/)
- [PostgreSQL Exercises](https://pgexercises.com/)