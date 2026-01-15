-- ЗАДАНИЕ:
-- Создайте materialized view `course_statistics_mv` со статистикой по каждому курсу:
-- название курса, количество студентов, средний балл, минимальный и максимальный балл

-- РЕШЕНИЕ:
CREATE MATERIALIZED VIEW course_statistics_mv AS
SELECT 
    c.id,
    c.title,
    COUNT(DISTINCT g.student_id) as students_count,
    ROUND(AVG(g.grade)::numeric, 2) as avg_grade,
    MIN(g.grade) as min_grade,
    MAX(g.grade) as max_grade
FROM courses c
LEFT JOIN grades g ON c.id = g.course_id
GROUP BY c.id, c.title
ORDER BY avg_grade DESC;

-- Проверка:
SELECT * FROM course_statistics_mv;

-- Обновление materialized view:
REFRESH MATERIALIZED VIEW course_statistics_mv;
