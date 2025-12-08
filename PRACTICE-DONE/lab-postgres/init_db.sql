-- Создание базы данных и таблиц
CREATE DATABASE lab_db;

-- Подключение к базе данных
\c lab_db;

-- Создание таблиц (если используется SQLAlchemy, то они создадутся автоматически)
-- Но для полноты добавим SQL для создания view

-- Создание представления активных студентов
CREATE OR REPLACE VIEW active_students_view AS
SELECT 
    s.id,
    s.name,
    s.email,
    s.status,
    s.created_at,
    COUNT(g.id) as grades_count,
    AVG(g.grade) as avg_grade
FROM students s
LEFT JOIN grades g ON s.id = g.student_id
WHERE s.status = 'active'
GROUP BY s.id, s.name, s.email, s.status, s.created_at;