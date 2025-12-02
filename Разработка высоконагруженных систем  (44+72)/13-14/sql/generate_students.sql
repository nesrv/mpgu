-- Генерация большого количества студентов (например, 10000)
INSERT INTO students (name, email, status)
SELECT 
    'Student ' || i,
    'student' || i || '@test.com',
    CASE WHEN i % 2 = 0 THEN 'active' ELSE 'inactive' END
FROM generate_series(1, 10000) AS i;
