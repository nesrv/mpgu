# 📝 Практические задания: Оконные функции PostgreSQL

**Время выполнения:** 2 часа  
**Уровень:** средний

---

## 📊 Подготовка данных

Создайте таблицы и заполните их данными:

```sql
-- Таблица продаж
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    product VARCHAR(50),
    category VARCHAR(50),
    region VARCHAR(50),
    sale_date DATE,
    amount DECIMAL(10,2)
);

INSERT INTO sales (product, category, region, sale_date, amount) VALUES
('iPhone 15', 'Электроника', 'Москва', '2025-01-01', 89990),
('Samsung S24', 'Электроника', 'Москва', '2025-01-02', 79990),
('MacBook Pro', 'Электроника', 'Москва', '2025-01-03', 199990),
('iPhone 15', 'Электроника', 'СПб', '2025-01-01', 89990),
('Холодильник LG', 'Бытовая техника', 'Москва', '2025-01-01', 45000),
('Стиральная машина', 'Бытовая техника', 'Москва', '2025-01-02', 35000),
('Холодильник Samsung', 'Бытовая техника', 'СПб', '2025-01-02', 48000),
('Микроволновка', 'Бытовая техника', 'СПб', '2025-01-03', 12000),
('iPhone 15', 'Электроника', 'Москва', '2025-01-04', 89990),
('Samsung S24', 'Электроника', 'СПб', '2025-01-04', 79990),
('MacBook Air', 'Электроника', 'Москва', '2025-01-05', 129990),
('Холодильник LG', 'Бытовая техника', 'СПб', '2025-01-05', 45000),
('Пылесос Dyson', 'Бытовая техника', 'Москва', '2025-01-06', 28000),
('iPhone 15', 'Электроника', 'СПб', '2025-01-06', 89990),
('Samsung S24', 'Электроника', 'Москва', '2025-01-07', 79990);

-- Таблица сотрудников
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(50),
    position VARCHAR(50),
    salary DECIMAL(10,2),
    hire_date DATE
);

INSERT INTO employees (name, department, position, salary, hire_date) VALUES
('Иванов Иван', 'IT', 'Junior Developer', 80000, '2023-01-15'),
('Петров Петр', 'IT', 'Middle Developer', 150000, '2022-03-20'),
('Сидорова Анна', 'IT', 'Senior Developer', 250000, '2020-05-10'),
('Козлов Дмитрий', 'IT', 'Team Lead', 300000, '2019-02-01'),
('Смирнова Мария', 'Продажи', 'Менеджер', 90000, '2023-06-01'),
('Новиков Алексей', 'Продажи', 'Старший менеджер', 140000, '2021-04-15'),
('Федорова Елена', 'Продажи', 'Директор', 280000, '2018-01-10'),
('Морозов Сергей', 'HR', 'Специалист', 85000, '2022-09-01'),
('Волкова Ольга', 'HR', 'Руководитель', 180000, '2020-03-15'),
('Соколов Андрей', 'Финансы', 'Бухгалтер', 95000, '2023-02-20'),
('Лебедева Татьяна', 'Финансы', 'Главный бухгалтер', 220000, '2019-07-01');
```

---

## 🎯 Блок 1: Базовые оконные функции (20 минут)

### Задание 1.1: Общая сумма продаж
**Задача:** Выведите все продажи с указанием общей суммы продаж по всем записям.

<details>
<summary>💡 Подсказка</summary>

Используйте `SUM() OVER()` без PARTITION BY

</details>

<details>
<summary>✅ Ответ</summary>

```sql
SELECT 
    product,
    amount,
    SUM(amount) OVER() as total_sales
FROM sales;
```

**Результат:**
```
┌─────────────────────┬──────────┬─────────────┐
│      product        │  amount  │ total_sales │
├─────────────────────┼──────────┼─────────────┤
│ iPhone 15           │  89990   │  1352940    │
│ Samsung S24         │  79990   │  1352940    │
│ MacBook Pro         │ 199990   │  1352940    │
│ Холодильник LG      │  45000   │  1352940    │
│ ...                 │   ...    │  1352940    │
└─────────────────────┴──────────┴─────────────┘
```
В каждой строке одинаковое значение total_sales

</details>

---

### Задание 1.2: Сумма продаж по категориям
**Задача:** Для каждой продажи выведите сумму продаж в её категории.

<details>
<summary>💡 Подсказка</summary>

Используйте `PARTITION BY category`

</details>

<details>
<summary>✅ Ответ</summary>

```sql
SELECT 
    product,
    category,
    amount,
    SUM(amount) OVER(PARTITION BY category) as category_total
FROM sales
ORDER BY category, product;
```

**Результат:**
```
┌─────────────────────┬─────────────────┬─────────┬────────────────┐
│      product        │    category     │ amount  │ category_total │
├─────────────────────┼─────────────────┼─────────┼────────────────┤
│ Микроволновка       │ Бытовая техника │  12000  │    213000      │
│ Пылесос Dyson       │ Бытовая техника │  28000  │    213000      │
│ Стиральная машина   │ Бытовая техника │  35000  │    213000      │
│ Холодильник LG      │ Бытовая техника │  45000  │    213000      │
│ Холодильник Samsung │ Бытовая техника │  48000  │    213000      │
├─────────────────────┼─────────────────┼─────────┼────────────────┤
│ iPhone 15           │ Электроника     │  89990  │   1139940      │
│ MacBook Air         │ Электроника     │ 129990  │   1139940      │
│ MacBook Pro         │ Электроника     │ 199990  │   1139940      │
│ Samsung S24         │ Электроника     │  79990  │   1139940      │
└─────────────────────┴─────────────────┴─────────┴────────────────┘
```

</details>

---

### Задание 1.3: Процент от общей суммы
**Задача:** Рассчитайте, какой процент от общей суммы продаж составляет каждая продажа.

<details>
<summary>✅ Ответ</summary>

```sql
SELECT 
    product,
    amount,
    ROUND(100.0 * amount / SUM(amount) OVER(), 2) as percent_of_total
FROM sales
ORDER BY percent_of_total DESC;
```

**Результат:**
```
┌─────────────────────┬─────────┬──────────────────┐
│      product        │ amount  │ percent_of_total │
├─────────────────────┼─────────┼──────────────────┤
│ MacBook Pro         │ 199990  │      15.5        │
│ MacBook Air         │ 129990  │       9.61       │
│ iPhone 15           │  89990  │       6.65       │
│ iPhone 15           │  89990  │       6.65       │
│ iPhone 15           │  89990  │       6.65       │
│ Samsung S24         │  79990  │       5.91       │
│ Холодильник Samsung │  48000  │       3.55       │
│ Холодильник LG      │  45000  │       3.33       │
└─────────────────────┴─────────┴──────────────────┘
```

</details>

---

## 🏆 Блок 2: Ранжирование (25 минут)

### Задание 2.1: Топ-3 продажи
**Задача:** Найдите топ-3 самых дорогих продажи с использованием ROW_NUMBER().

<details>
<summary>✅ Ответ</summary>

```sql
SELECT * FROM (
    SELECT 
        product,
        amount,
        ROW_NUMBER() OVER(ORDER BY amount DESC) as row_num
    FROM sales
) t WHERE row_num <= 3;
```

**Результат:**
```
┌─────────────────┬─────────┬─────────┐
│    product      │ amount  │ row_num │
├─────────────────┼─────────┼─────────┤
│ MacBook Pro     │ 199990  │    1    │
│ MacBook Air     │ 129990  │    2    │
│ iPhone 15       │  89990  │    3    │
└─────────────────┴─────────┴─────────┘
```

</details>

---

### Задание 2.2: Ранжирование сотрудников по зарплате
**Задача:** Выведите сотрудников с их рангом по зарплате в каждом отделе. Используйте RANK(), DENSE_RANK() и ROW_NUMBER() для сравнения.

<details>
<summary>✅ Ответ</summary>

```sql
SELECT 
    name,
    department,
    salary,
    ROW_NUMBER() OVER(PARTITION BY department ORDER BY salary DESC) as row_num,
    RANK() OVER(PARTITION BY department ORDER BY salary DESC) as rank,
    DENSE_RANK() OVER(PARTITION BY department ORDER BY salary DESC) as dense_rank
FROM employees
ORDER BY department, salary DESC;
```

**Результат:**
```
┌─────────────────┬────────────┬────────┬─────────┬──────┬────────────┐
│      name       │ department │ salary │ row_num │ rank │ dense_rank │
├─────────────────┼────────────┼────────┼─────────┼──────┼────────────┤
│ Соколов Андрей  │ Финансы    │ 220000 │    1    │  1   │     1      │
│ Лебедева Татьяна│ Финансы    │  95000 │    2    │  2   │     2      │
├─────────────────┼────────────┼────────┼─────────┼──────┼────────────┤
│ Козлов Дмитрий  │     IT     │ 300000 │    1    │  1   │     1      │
│ Сидорова Анна   │     IT     │ 250000 │    2    │  2   │     2      │
│ Петров Петр     │     IT     │ 150000 │    3    │  3   │     3      │
│ Иванов Иван     │     IT     │  80000 │    4    │  4   │     4      │
└─────────────────┴────────────┴────────┴─────────┴──────┴────────────┘
```

</details>

---

### Задание 2.3: Квартили зарплат
**Задача:** Разделите всех сотрудников на 4 группы (квартили) по уровню зарплаты.

<details>
<summary>💡 Подсказка</summary>

Используйте NTILE(4)

</details>

<details>
<summary>✅ Ответ</summary>

```sql
SELECT 
    name,
    salary,
    NTILE(4) OVER(ORDER BY salary DESC) as salary_quartile
FROM employees
ORDER BY salary DESC;
```

**Результат:**
```
┌─────────────────┬────────┬─────────────────┐
│      name       │ salary │ salary_quartile │
├─────────────────┼────────┼─────────────────┤
│ Козлов Дмитрий  │ 300000 │        1        │ ← Топ 25%
│ Федорова Елена  │ 280000 │        1        │
│ Сидорова Анна   │ 250000 │        1        │
├─────────────────┼────────┼─────────────────┤
│ Соколов Андрей  │ 220000 │        2        │
│ Волкова Ольга   │ 180000 │        2        │
│ Петров Петр     │ 150000 │        2        │
├─────────────────┼────────┼─────────────────┤
│ Новиков Алексей │ 140000 │        3        │
│ Лебедева Татьяна│  95000 │        3        │
├─────────────────┼────────┼─────────────────┤
│ Смирнова Мария  │  90000 │        4        │ ← Нижние 25%
│ Морозов Сергей  │  85000 │        4        │
│ Иванов Иван     │  80000 │        4        │
└─────────────────┴────────┴─────────────────┘
```

</details>

---

## 📈 Блок 3: Нарастающий итог и скользящие окна (30 минут)

### Задание 3.1: Нарастающий итог продаж по дням
**Задача:** Рассчитайте накопленную сумму продаж по дням.

<details>
<summary>✅ Ответ</summary>

```sql
SELECT 
    sale_date,
    SUM(amount) as daily_sales,
    SUM(SUM(amount)) OVER(ORDER BY sale_date) as running_total
FROM sales
GROUP BY sale_date
ORDER BY sale_date;
```

**Результат:**
```
┌────────────┬─────────────┬───────────────┐
│ sale_date  │ daily_sales │ running_total │
├────────────┼─────────────┼───────────────┤
│ 2025-01-01 │   269980    │    269980     │
│ 2025-01-02 │   242990    │    512970     │
│ 2025-01-03 │   211990    │    724960     │
│ 2025-01-04 │   169980    │    894940     │
│ 2025-01-05 │   174990    │   1069930     │
│ 2025-01-06 │   117990    │   1187920     │
│ 2025-01-07 │    79990    │   1267910     │
└────────────┴─────────────┴───────────────┘
```

</details>

---

### Задание 3.2: Нарастающий итог по категориям
**Задача:** Рассчитайте накопленную сумму продаж по дням отдельно для каждой категории.

<details>
<summary>✅ Ответ</summary>

```sql
SELECT 
    category,
    sale_date,
    SUM(amount) as daily_sales,
    SUM(SUM(amount)) OVER(
        PARTITION BY category 
        ORDER BY sale_date
    ) as category_running_total
FROM sales
GROUP BY category, sale_date
ORDER BY category, sale_date;
```

</details>

---

### Задание 3.3: Скользящее среднее за 3 дня
**Задача:** Рассчитайте среднюю сумму продаж за последние 3 дня (включая текущий).

<details>
<summary>✅ Ответ</summary>

```sql
SELECT 
    sale_date,
    SUM(amount) as daily_sales,
    ROUND(AVG(SUM(amount)) OVER(
        ORDER BY sale_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) as moving_avg_3days
FROM sales
GROUP BY sale_date
ORDER BY sale_date;
```

</details>

---

### Задание 3.4: Сумма за последние 7 дней
**Задача:** Для каждого дня рассчитайте сумму продаж за последние 7 дней.

<details>
<summary>✅ Ответ</summary>

```sql
SELECT 
    sale_date,
    SUM(amount) as daily_sales,
    SUM(SUM(amount)) OVER(
        ORDER BY sale_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as last_7days_sales
FROM sales
GROUP BY sale_date
ORDER BY sale_date;
```

</details>

---

## ⬅️➡️ Блок 4: LAG и LEAD (20 минут)

### Задание 4.1: Сравнение с предыдущим днём
**Задача:** Для каждого дня выведите сумму продаж, сумму за предыдущий день и разницу между ними.

<details>
<summary>✅ Ответ</summary>

```sql
SELECT 
    sale_date,
    SUM(amount) as daily_sales,
    LAG(SUM(amount)) OVER(ORDER BY sale_date) as prev_day_sales,
    SUM(amount) - LAG(SUM(amount)) OVER(ORDER BY sale_date) as diff
FROM sales
GROUP BY sale_date
ORDER BY sale_date;
```

**Результат:**
```
┌────────────┬─────────────┬────────────────┬─────────┐
│ sale_date  │ daily_sales │ prev_day_sales │   diff  │
├────────────┼─────────────┼────────────────┼─────────┤
│ 2025-01-01 │   269980    │      NULL      │   NULL  │
│ 2025-01-02 │   242990    │     269980     │  -26990 │
│ 2025-01-03 │   211990    │     242990     │  -31000 │
│ 2025-01-04 │   169980    │     211990     │  -42010 │
│ 2025-01-05 │   174990    │     169980     │   +5010 │
│ 2025-01-06 │   117990    │     174990     │  -57000 │
│ 2025-01-07 │    79990    │     117990     │  -38000 │
└────────────┴─────────────┴────────────────┴─────────┘
```

</details>

---

### Задание 4.2: Процент роста продаж
**Задача:** Рассчитайте процент изменения продаж по сравнению с предыдущим днём.

<details>
<summary>✅ Ответ</summary>

```sql
SELECT 
    sale_date,
    SUM(amount) as daily_sales,
    LAG(SUM(amount)) OVER(ORDER BY sale_date) as prev_day_sales,
    ROUND(
        100.0 * (SUM(amount) - LAG(SUM(amount)) OVER(ORDER BY sale_date)) / 
        LAG(SUM(amount)) OVER(ORDER BY sale_date), 
        2
    ) as growth_percent
FROM sales
GROUP BY sale_date
ORDER BY sale_date;
```

</details>

---

### Задание 4.3: Следующая зарплата в отделе
**Задача:** Для каждого сотрудника выведите зарплату следующего по уровню сотрудника в его отделе.

<details>
<summary>✅ Ответ</summary>

```sql
SELECT 
    name,
    department,
    salary,
    LEAD(salary) OVER(PARTITION BY department ORDER BY salary DESC) as next_salary,
    salary - LEAD(salary) OVER(PARTITION BY department ORDER BY salary DESC) as diff
FROM employees
ORDER BY department, salary DESC;
```

</details>

---

## 🎲 Блок 5: Группировки GROUPING SETS, ROLLUP, CUBE (25 минут)

### Задание 5.1: GROUPING SETS — итоги по разным срезам
**Задача:** Получите итоги продаж по категориям, по регионам и общий итог одним запросом.

<details>
<summary>✅ Ответ</summary>

```sql
SELECT 
    category,
    region,
    SUM(amount) as total
FROM sales
GROUP BY GROUPING SETS (
    (category),
    (region),
    ()
)
ORDER BY category NULLS LAST, region NULLS LAST;
```

**Результат:**
```
┌─────────────────┬────────┬──────────┐
│    category     │ region │  total   │
├─────────────────┼────────┼──────────┤
│ Бытовая техника │  NULL  │  213000  │ ← Итог по категории
│ Электроника     │  NULL  │ 1139940  │ ← Итог по категории
├─────────────────┼────────┼──────────┤
│      NULL       │ Москва │  692960  │ ← Итог по региону
│      NULL       │  СПб  │  659980  │ ← Итог по региону
├─────────────────┼────────┼──────────┤
│      NULL       │  NULL  │ 1352940  │ ← Общий итог
└─────────────────┴────────┴──────────┘
```

</details>

---

### Задание 5.2: ROLLUP — иерархические итоги
**Задача:** Получите иерархические итоги: по категориям и регионам, только по категориям, общий итог.

<details>
<summary>✅ Ответ</summary>

```sql
SELECT 
    category,
    region,
    SUM(amount) as total,
    COUNT(*) as sales_count
FROM sales
GROUP BY ROLLUP(category, region)
ORDER BY category NULLS LAST, region NULLS LAST;
```

**Результат:**
- Детализация: категория + регион
- Промежуточные итоги: только категория
- Общий итог: оба NULL

</details>

---

### Задание 5.3: CUBE — все комбинации
**Задача:** Получите все возможные комбинации группировок по категориям и регионам.

<details>
<summary>✅ Ответ</summary>

```sql
SELECT 
    category,
    region,
    SUM(amount) as total,
    COUNT(*) as sales_count
FROM sales
GROUP BY CUBE(category, region)
ORDER BY category NULLS LAST, region NULLS LAST;
```

**Результат:**
- (category, region) — детализация
- (category, NULL) — итоги по категориям
- (NULL, region) — итоги по регионам
- (NULL, NULL) — общий итог

</details>

---

## 🔥 Блок 6: Комплексные задачи (20 минут)

### Задание 6.1: Топ-2 товара в каждой категории
**Задача:** Найдите 2 самых продаваемых товара (по сумме) в каждой категории.

<details>
<summary>✅ Ответ</summary>

```sql
SELECT * FROM (
    SELECT 
        category,
        product,
        SUM(amount) as total_sales,
        RANK() OVER(PARTITION BY category ORDER BY SUM(amount) DESC) as rank
    FROM sales
    GROUP BY category, product
) t 
WHERE rank <= 2
ORDER BY category, rank;
```

**Результат:**
```
┌─────────────────┬─────────────────────┬─────────────┬──────┐
│    category     │      product        │ total_sales │ rank │
├─────────────────┼─────────────────────┼─────────────┼──────┤
│ Бытовая техника │ Холодильник LG      │    90000    │  1   │
│ Бытовая техника │ Холодильник Samsung │    48000    │  2   │
├─────────────────┼─────────────────────┼─────────────┼──────┤
│ Электроника     │ iPhone 15           │   359960    │  1   │
│ Электроника     │ Samsung S24         │   239970    │  2   │
└─────────────────┴─────────────────────┴─────────────┴──────┘
```

</details>

---

### Задание 6.2: Анализ динамики продаж
**Задача:** Для каждого дня выведите:
- Сумму продаж
- Нарастающий итог
- Скользящее среднее за 3 дня
- Процент от общей суммы

<details>
<summary>✅ Ответ</summary>

```sql
SELECT 
    sale_date,
    SUM(amount) as daily_sales,
    SUM(SUM(amount)) OVER(ORDER BY sale_date) as running_total,
    ROUND(AVG(SUM(amount)) OVER(
        ORDER BY sale_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) as moving_avg_3days,
    ROUND(100.0 * SUM(amount) / SUM(SUM(amount)) OVER(), 2) as percent_of_total
FROM sales
GROUP BY sale_date
ORDER BY sale_date;
```

</details>

---

### Задание 6.3: Сравнение регионов
**Задача:** Для каждого региона выведите:
- Общую сумму продаж
- Ранг региона по продажам
- Процент от общей суммы
- Разницу с лидером

<details>
<summary>✅ Ответ</summary>

```sql
SELECT 
    region,
    SUM(amount) as total_sales,
    RANK() OVER(ORDER BY SUM(amount) DESC) as rank,
    ROUND(100.0 * SUM(amount) / SUM(SUM(amount)) OVER(), 2) as percent,
    FIRST_VALUE(SUM(amount)) OVER(ORDER BY SUM(amount) DESC) - SUM(amount) as diff_from_leader
FROM sales
GROUP BY region
ORDER BY total_sales DESC;
```

</details>

---

### Задание 6.4: Зарплатная аналитика
**Задача:** Для каждого сотрудника выведите:
- Его зарплату
- Среднюю зарплату в отделе
- Разницу с средней
- Ранг в отделе
- Процент от фонда оплаты труда отдела

<details>
<summary>✅ Ответ</summary>

```sql
SELECT 
    name,
    department,
    salary,
    ROUND(AVG(salary) OVER(PARTITION BY department), 2) as dept_avg_salary,
    ROUND(salary - AVG(salary) OVER(PARTITION BY department), 2) as diff_from_avg,
    RANK() OVER(PARTITION BY department ORDER BY salary DESC) as rank_in_dept,
    ROUND(100.0 * salary / SUM(salary) OVER(PARTITION BY department), 2) as percent_of_dept_budget
FROM employees
ORDER BY department, salary DESC;
```

</details>

---

## 🎓 Дополнительное задание (бонус)

### Задание 7: Когортный анализ продаж
**Задача:** Для каждой категории товаров рассчитайте:
1. Первый день продаж (когорта)
2. Количество дней с момента первой продажи
3. Накопленную сумму продаж с первого дня

<details>
<summary>✅ Ответ</summary>

```sql
SELECT 
    category,
    sale_date,
    SUM(amount) as daily_sales,
    FIRST_VALUE(sale_date) OVER(PARTITION BY category ORDER BY sale_date) as cohort_date,
    sale_date - FIRST_VALUE(sale_date) OVER(PARTITION BY category ORDER BY sale_date) as days_since_first,
    SUM(SUM(amount)) OVER(PARTITION BY category ORDER BY sale_date) as cumulative_sales
FROM sales
GROUP BY category, sale_date
ORDER BY category, sale_date;
```

</details>

---


**Удачи! 🚀**
