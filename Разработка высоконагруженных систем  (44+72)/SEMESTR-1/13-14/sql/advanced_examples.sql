-- ============================================
-- ПРОДВИНУТЫЕ ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ХРАНИМЫХ ОБЪЕКТОВ
-- ============================================

-- 1. ФУНКЦИЯ: Рекомендация курсов на основе успеваемости
-- Возвращает курсы, которые студент еще не проходил, но подходят по уровню
CREATE OR REPLACE FUNCTION recommend_courses(p_student_id INT)
RETURNS TABLE(
    course_id INT,
    course_title VARCHAR,
    avg_grade_of_others NUMERIC,
    reason TEXT
)
LANGUAGE sql
AS $$
    SELECT 
        c.id,
        c.title,
        ROUND(AVG(g.grade)::numeric, 2) as avg_grade,
        CASE 
            WHEN AVG(g.grade) >= 4.5 THEN 'Высокий уровень - подходит для отличников'
            WHEN AVG(g.grade) >= 3.5 THEN 'Средний уровень - подходит для большинства'
            ELSE 'Базовый уровень - для начинающих'
        END as reason
    FROM courses c
    LEFT JOIN grades g ON c.id = g.course_id
    WHERE c.id NOT IN (
        SELECT course_id FROM grades WHERE student_id = p_student_id
    )
    GROUP BY c.id, c.title
    ORDER BY avg_grade DESC;
$$;

-- Использование:
SELECT * FROM recommend_courses(1);


-- 2. MATERIALIZED VIEW: Рейтинг студентов с обновлением раз в час
CREATE MATERIALIZED VIEW student_leaderboard_mv AS
SELECT 
    ROW_NUMBER() OVER (ORDER BY AVG(g.grade) DESC) as rank,
    s.id,
    s.name,
    s.email,
    ROUND(AVG(g.grade)::numeric, 2) as gpa,
    COUNT(DISTINCT g.course_id) as courses_completed,
    CASE 
        WHEN AVG(g.grade) >= 4.8 THEN '🏆 Золото'
        WHEN AVG(g.grade) >= 4.5 THEN '🥈 Серебро'
        WHEN AVG(g.grade) >= 4.0 THEN '🥉 Бронза'
        ELSE '📚 Участник'
    END as badge
FROM students s
JOIN grades g ON s.id = g.student_id
WHERE s.status = 'active'
GROUP BY s.id, s.name, s.email
ORDER BY gpa DESC;

-- Проверка:
SELECT * FROM student_leaderboard_mv;


-- 3. ПРОЦЕДУРА: Массовое зачисление студентов на курс
CREATE OR REPLACE PROCEDURE enroll_students_to_course(
    p_course_id INT,
    p_min_gpa NUMERIC DEFAULT 4.0
)
LANGUAGE sql
AS $$
    INSERT INTO grades (student_id, course_id, grade)
    SELECT 
        s.id,
        p_course_id,
        0  -- Начальная оценка
    FROM students s
    WHERE s.status = 'active'
    AND s.id NOT IN (
        SELECT student_id FROM grades WHERE course_id = p_course_id
    )
    AND (
        SELECT COALESCE(AVG(grade), 0) 
        FROM grades 
        WHERE student_id = s.id
    ) >= p_min_gpa;
$$;

-- Вызов:
CALL enroll_students_to_course(1, 4.5);


-- 4. ФУНКЦИЯ: Анализ сложности курса
CREATE OR REPLACE FUNCTION analyze_course_difficulty(p_course_id INT)
RETURNS TABLE(
    course_title VARCHAR,
    avg_grade NUMERIC,
    pass_rate NUMERIC,
    difficulty_level TEXT,
    recommendation TEXT
)
LANGUAGE sql
AS $$
    SELECT 
        c.title,
        ROUND(AVG(g.grade)::numeric, 2),
        ROUND((COUNT(*) FILTER (WHERE g.grade >= 3.0)::NUMERIC / COUNT(*) * 100), 2) as pass_rate,
        CASE 
            WHEN AVG(g.grade) < 3.5 THEN 'Сложный'
            WHEN AVG(g.grade) < 4.0 THEN 'Средний'
            ELSE 'Легкий'
        END,
        CASE 
            WHEN AVG(g.grade) < 3.5 THEN 'Требуется дополнительная поддержка студентов'
            WHEN AVG(g.grade) < 4.0 THEN 'Курс сбалансирован'
            ELSE 'Можно усложнить программу'
        END
    FROM courses c
    JOIN grades g ON c.id = g.course_id
    WHERE c.id = p_course_id
    GROUP BY c.id, c.title;
$$;

-- Использование:
SELECT * FROM analyze_course_difficulty(1);


-- 5. VIEW: Студенты в зоне риска (низкая успеваемость)
CREATE VIEW at_risk_students_view AS
SELECT 
    s.id,
    s.name,
    s.email,
    ROUND(AVG(g.grade)::numeric, 2) as gpa,
    COUNT(g.id) FILTER (WHERE g.grade < 3.0) as failing_courses,
    ARRAY_AGG(c.title) FILTER (WHERE g.grade < 3.0) as problem_courses
FROM students s
JOIN grades g ON s.id = g.student_id
JOIN courses c ON g.course_id = c.id
WHERE s.status = 'active'
GROUP BY s.id, s.name, s.email
HAVING AVG(g.grade) < 3.5 OR COUNT(g.id) FILTER (WHERE g.grade < 3.0) > 0
ORDER BY gpa ASC;

-- Проверка:
SELECT * FROM at_risk_students_view;


-- 6. ФУНКЦИЯ: Прогноз итоговой оценки
CREATE OR REPLACE FUNCTION predict_final_grade(
    p_student_id INT,
    p_course_id INT,
    p_current_progress NUMERIC  -- процент выполнения курса (0-100)
)
RETURNS NUMERIC
LANGUAGE sql
STABLE
AS $$
    SELECT 
        ROUND(
            (
                SELECT COALESCE(AVG(grade), 4.0)
                FROM grades
                WHERE student_id = p_student_id
            ) * (p_current_progress / 100) + 
            (
                SELECT COALESCE(AVG(grade), 4.0)
                FROM grades
                WHERE course_id = p_course_id
            ) * (1 - p_current_progress / 100)
        , 2);
$$;

-- Использование:
SELECT 
    s.name,
    c.title,
    predict_final_grade(s.id, c.id, 75) as predicted_grade
FROM students s
CROSS JOIN courses c
WHERE s.id = 1 AND c.id = 1;


-- 7. ПРОЦЕДУРА: Автоматическое обновление статусов
CREATE OR REPLACE PROCEDURE update_student_statuses()
LANGUAGE sql
AS $$
    UPDATE students
    SET status = CASE
        WHEN (
            SELECT COALESCE(AVG(grade), 0)
            FROM grades
            WHERE student_id = students.id
        ) < 3.0 THEN 'probation'
        WHEN (
            SELECT COALESCE(AVG(grade), 0)
            FROM grades
            WHERE student_id = students.id
        ) >= 4.5 THEN 'honors'
        ELSE 'active'
    END
    WHERE id IN (SELECT DISTINCT student_id FROM grades);
$$;

-- Вызов:
CALL update_student_statuses();


-- 8. ФУНКЦИЯ: Топ курсов по популярности и качеству
CREATE OR REPLACE FUNCTION get_trending_courses(p_limit INT DEFAULT 5)
RETURNS TABLE(
    course_id INT,
    course_title VARCHAR,
    students_count BIGINT,
    avg_grade NUMERIC,
    popularity_score NUMERIC
)
LANGUAGE sql
AS $$
    SELECT 
        c.id,
        c.title,
        COUNT(DISTINCT g.student_id),
        ROUND(AVG(g.grade)::numeric, 2),
        ROUND((COUNT(DISTINCT g.student_id) * AVG(g.grade))::numeric, 2) as score
    FROM courses c
    JOIN grades g ON c.id = g.course_id
    GROUP BY c.id, c.title
    ORDER BY score DESC
    LIMIT p_limit;
$$;

-- Использование:
SELECT * FROM get_trending_courses(3);


-- 9. VIEW: Статистика по дням недели
CREATE VIEW weekly_performance_view AS
SELECT 
    EXTRACT(DOW FROM s.created_at) as day_of_week,
    CASE EXTRACT(DOW FROM s.created_at)
        WHEN 0 THEN 'Воскресенье'
        WHEN 1 THEN 'Понедельник'
        WHEN 2 THEN 'Вторник'
        WHEN 3 THEN 'Среда'
        WHEN 4 THEN 'Четверг'
        WHEN 5 THEN 'Пятница'
        WHEN 6 THEN 'Суббота'
    END as day_name,
    COUNT(DISTINCT s.id) as students_registered,
    ROUND(AVG(g.grade)::numeric, 2) as avg_grade
FROM students s
LEFT JOIN grades g ON s.id = g.student_id
GROUP BY EXTRACT(DOW FROM s.created_at)
ORDER BY day_of_week;


-- 10. ФУНКЦИЯ: Генерация отчета по студенту
CREATE OR REPLACE FUNCTION generate_student_report(p_student_id INT)
RETURNS TABLE(
    student_name VARCHAR,
    total_courses BIGINT,
    gpa NUMERIC,
    best_course VARCHAR,
    worst_course VARCHAR,
    status TEXT,
    recommendation TEXT
)
LANGUAGE sql
AS $$
    SELECT 
        s.name,
        COUNT(g.id),
        ROUND(AVG(g.grade)::numeric, 2),
        (SELECT c.title FROM courses c JOIN grades g2 ON c.id = g2.course_id 
         WHERE g2.student_id = p_student_id ORDER BY g2.grade DESC LIMIT 1),
        (SELECT c.title FROM courses c JOIN grades g2 ON c.id = g2.course_id 
         WHERE g2.student_id = p_student_id ORDER BY g2.grade ASC LIMIT 1),
        CASE 
            WHEN AVG(g.grade) >= 4.5 THEN 'Отличник'
            WHEN AVG(g.grade) >= 4.0 THEN 'Хорошист'
            WHEN AVG(g.grade) >= 3.0 THEN 'Удовлетворительно'
            ELSE 'Требуется помощь'
        END,
        CASE 
            WHEN AVG(g.grade) >= 4.5 THEN 'Продолжайте в том же духе!'
            WHEN AVG(g.grade) >= 4.0 THEN 'Хорошая работа, стремитесь к большему'
            WHEN AVG(g.grade) >= 3.0 THEN 'Уделите больше времени учебе'
            ELSE 'Обратитесь к куратору за помощью'
        END
    FROM students s
    LEFT JOIN grades g ON s.id = g.student_id
    WHERE s.id = p_student_id
    GROUP BY s.id, s.name;
$$;

-- Использование:
SELECT * FROM generate_student_report(1);
