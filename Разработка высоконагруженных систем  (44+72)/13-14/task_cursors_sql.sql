-- ============================================
-- ЗАДАНИЕ 1: Работа с курсором в транзакции
-- ============================================
-- Создайте курсор для чтения активных студентов и прочитайте первые 5 записей

-- РЕШЕНИЕ 1:
BEGIN;

DECLARE student_cursor CURSOR FOR 
    SELECT id, name, email FROM students WHERE status = 'active';

-- Читаем первые 5 записей
FETCH 5 FROM student_cursor;

-- Читаем следующие 5
FETCH 5 FROM student_cursor;

CLOSE student_cursor;
COMMIT;


-- ============================================
-- ЗАДАНИЕ 2: SCROLL курсор для навигации
-- ============================================
-- Создайте SCROLL курсор и продемонстрируйте навигацию

-- РЕШЕНИЕ 2:
BEGIN;

DECLARE nav_cursor SCROLL CURSOR FOR 
    SELECT id, name FROM students ORDER BY id;

-- Первая запись
FETCH FIRST FROM nav_cursor;

-- Последняя запись
FETCH LAST FROM nav_cursor;

-- 5-я запись
FETCH ABSOLUTE 5 FROM nav_cursor;

-- Назад на 2 записи
FETCH PRIOR FROM nav_cursor;
FETCH PRIOR FROM nav_cursor;

CLOSE nav_cursor;
COMMIT;


-- ============================================
-- ЗАДАНИЕ 3: Курсор для больших данных
-- ============================================
-- Создайте курсор для чтения всех оценок порциями по 1000 записей

-- РЕШЕНИЕ 3:
BEGIN;

DECLARE grades_cursor CURSOR FOR 
    SELECT g.id, s.name, c.title, g.grade
    FROM grades g
    JOIN students s ON g.student_id = s.id
    JOIN courses c ON g.course_id = c.id
    ORDER BY g.id;

-- Читаем первую порцию (1000 записей)
FETCH 1000 FROM grades_cursor;

-- Читаем вторую порцию
FETCH 1000 FROM grades_cursor;

-- Читаем третью порцию
FETCH 1000 FROM grades_cursor;

CLOSE grades_cursor;
COMMIT;
