-- ============================================
-- ЗАДАНИЕ 1: Процедура добавления студента
-- ============================================
-- Создайте процедуру add_student для добавления нового студента

-- РЕШЕНИЕ 1:
CREATE OR REPLACE PROCEDURE add_student(
    p_name VARCHAR,
    p_email VARCHAR,
    p_status VARCHAR DEFAULT 'active'
)
LANGUAGE sql
AS $$
    INSERT INTO students (name, email, status)
    VALUES (p_name, p_email, p_status);
$$;

-- Вызов:
CALL add_student('Петр Петров', 'petr.petrov@example.com', 'active');


-- ============================================
-- ЗАДАНИЕ 2: Процедура добавления оценки
-- ============================================
-- Создайте процедуру add_grade для добавления оценки студенту по курсу

-- РЕШЕНИЕ 2:
CREATE OR REPLACE PROCEDURE add_grade(
    p_student_id INT,
    p_course_id INT,
    p_grade REAL
)
LANGUAGE sql
AS $$
    INSERT INTO grades (student_id, course_id, grade)
    VALUES (p_student_id, p_course_id, p_grade);
$$;

-- Вызов:
CALL add_grade(1, 1, 4.5);


-- ============================================
-- ЗАДАНИЕ 3: Процедура обновления статуса
-- ============================================
-- Создайте процедуру update_student_status для изменения статуса студента

-- РЕШЕНИЕ 3:
CREATE OR REPLACE PROCEDURE update_student_status(
    p_student_id INT,
    p_new_status VARCHAR
)
LANGUAGE sql
AS $$
    UPDATE students 
    SET status = p_new_status
    WHERE id = p_student_id;
$$;

-- Вызов:
CALL update_student_status(1, 'inactive');


-- ============================================
-- ЗАДАНИЕ 4: Процедура удаления старых записей
-- ============================================
-- Создайте процедуру delete_inactive_students для удаления неактивных студентов без оценок

-- РЕШЕНИЕ 4:
CREATE OR REPLACE PROCEDURE delete_inactive_students()
LANGUAGE sql
AS $$
    DELETE FROM students
    WHERE status = 'inactive'
    AND id NOT IN (SELECT DISTINCT student_id FROM grades);
$$;

-- Вызов:
CALL delete_inactive_students();
