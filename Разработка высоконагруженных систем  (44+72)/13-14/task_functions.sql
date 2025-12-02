-- ============================================
-- ЗАДАНИЕ 1: Функция расчета среднего балла студента
-- ============================================
-- Создайте функцию get_student_avg_grade, которая возвращает средний балл студента по его ID

-- РЕШЕНИЕ 1:
CREATE OR REPLACE FUNCTION get_student_avg_grade(p_student_id INT)
RETURNS NUMERIC
LANGUAGE sql
AS $$
    SELECT COALESCE(ROUND(AVG(grade)::numeric, 2), 0)
    FROM grades
    WHERE student_id = p_student_id;
$$;

-- Использование:
SELECT name, get_student_avg_grade(id) as avg_grade
FROM students;


-- ============================================
-- ЗАДАНИЕ 2: Функция подсчета курсов студента
-- ============================================
-- Создайте функцию count_student_courses, которая возвращает количество курсов студента

-- РЕШЕНИЕ 2:
CREATE OR REPLACE FUNCTION count_student_courses(p_student_id INT)
RETURNS BIGINT
LANGUAGE sql
AS $$
    SELECT COUNT(DISTINCT course_id)
    FROM grades
    WHERE student_id = p_student_id;
$$;

-- Использование:
SELECT name, count_student_courses(id) as courses_count
FROM students;


-- ============================================
-- ЗАДАНИЕ 3: Функция получения статуса по баллу
-- ============================================
-- Создайте функцию get_grade_status, которая возвращает статус оценки:
-- 'Отлично' (>=4.5), 'Хорошо' (>=3.5), 'Удовлетворительно' (<3.5)

-- РЕШЕНИЕ 3:
CREATE OR REPLACE FUNCTION get_grade_status(p_grade REAL)
RETURNS TEXT
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT CASE
        WHEN p_grade >= 4.5 THEN 'Отлично'
        WHEN p_grade >= 3.5 THEN 'Хорошо'
        ELSE 'Удовлетворительно'
    END;
$$;

-- Использование:
SELECT s.name, c.title, g.grade, get_grade_status(g.grade) as status
FROM grades g
JOIN students s ON g.student_id = s.id
JOIN courses c ON g.course_id = c.id;


-- ============================================
-- ЗАДАНИЕ 4: Функция возвращающая таблицу студентов курса
-- ============================================
-- Создайте функцию get_course_students, которая возвращает всех студентов курса

-- РЕШЕНИЕ 4:
CREATE OR REPLACE FUNCTION get_course_students(p_course_id INT)
RETURNS TABLE(
    student_id INT,
    student_name VARCHAR,
    student_email VARCHAR,
    grade REAL
)
LANGUAGE sql
AS $$
    SELECT s.id, s.name, s.email, g.grade
    FROM students s
    JOIN grades g ON s.id = g.student_id
    WHERE g.course_id = p_course_id
    ORDER BY g.grade DESC;
$$;

-- Использование:
SELECT * FROM get_course_students(1);


-- ============================================
-- ЗАДАНИЕ 5: Функция расчета скидки на курс
-- ============================================
-- Создайте функцию calculate_course_discount, которая возвращает цену курса со скидкой
-- Скидка 10% если credits >= 4, иначе без скидки. Базовая цена: 1000 за credit

-- РЕШЕНИЕ 5:
CREATE OR REPLACE FUNCTION calculate_course_discount(p_course_id INT)
RETURNS NUMERIC
LANGUAGE sql
STABLE
AS $$
    SELECT 
        CASE 
            WHEN credits >= 4 THEN credits * 1000 * 0.9
            ELSE credits * 1000
        END
    FROM courses
    WHERE id = p_course_id;
$$;

-- Использование:
SELECT 
    title, 
    credits,
    credits * 1000 as original_price,
    calculate_course_discount(id) as discounted_price
FROM courses;
