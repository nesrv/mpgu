-- ЗАДАНИЕ:
-- Создайте view `top_students_view` с топ-10 студентами по среднему баллу

-- РЕШЕНИЕ:
CREATE VIEW top_students_view AS
SELECT 
    s.id,
    s.name,
    s.email,
    ROUND(AVG(g.grade)::numeric, 2) as avg_grade,
    COUNT(g.id) as courses_count
FROM students s
JOIN grades g ON s.id = g.student_id
GROUP BY s.id, s.name, s.email
ORDER BY avg_grade DESC
LIMIT 5;

-- Проверка:
SELECT * FROM top_students_view;
