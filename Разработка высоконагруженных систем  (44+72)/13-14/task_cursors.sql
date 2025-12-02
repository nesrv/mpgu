-- ============================================
-- ЗАДАНИЕ 1: Обработка студентов порциями
-- ============================================
-- Создайте курсор для чтения всех активных студентов порциями по 100 записей
-- и выведите их имена

-- РЕШЕНИЕ 1:
DO $$
DECLARE
    student_cursor CURSOR FOR 
        SELECT id, name, email FROM students WHERE status = 'active';
    student_record RECORD;
    counter INT := 0;
BEGIN
    OPEN student_cursor;
    
    LOOP
        FETCH student_cursor INTO student_record;
        EXIT WHEN NOT FOUND;
        
        RAISE NOTICE 'Student: % (ID: %)', student_record.name, student_record.id;
        counter := counter + 1;
        
        -- Коммит каждые 100 записей
        IF counter % 100 = 0 THEN
            RAISE NOTICE 'Processed % students', counter;
        END IF;
    END LOOP;
    
    CLOSE student_cursor;
    RAISE NOTICE 'Total processed: % students', counter;
END $$;


-- ============================================
-- ЗАДАНИЕ 2: Навигация по курсору
-- ============================================
-- Создайте SCROLL курсор для студентов и продемонстрируйте навигацию:
-- первая запись, последняя запись, 5-я запись

-- РЕШЕНИЕ 2:
DO $$
DECLARE
    nav_cursor SCROLL CURSOR FOR 
        SELECT id, name FROM students ORDER BY id;
    student_rec RECORD;
BEGIN
    OPEN nav_cursor;
    
    -- Первая запись
    FETCH FIRST FROM nav_cursor INTO student_rec;
    RAISE NOTICE 'First student: % (ID: %)', student_rec.name, student_rec.id;
    
    -- Последняя запись
    FETCH LAST FROM nav_cursor INTO student_rec;
    RAISE NOTICE 'Last student: % (ID: %)', student_rec.name, student_rec.id;
    
    -- 5-я запись
    FETCH ABSOLUTE 5 FROM nav_cursor INTO student_rec;
    RAISE NOTICE '5th student: % (ID: %)', student_rec.name, student_rec.id;
    
    CLOSE nav_cursor;
END $$;


-- ============================================
-- ЗАДАНИЕ 3: Обновление через курсор
-- ============================================
-- Создайте курсор для студентов с низким средним баллом (< 4.0)
-- и обновите их статус на 'needs_attention'

-- РЕШЕНИЕ 3:
DO $$
DECLARE
    low_gpa_cursor CURSOR FOR 
        SELECT s.id, s.name, AVG(g.grade) as avg_grade
        FROM students s
        JOIN grades g ON s.id = g.student_id
        GROUP BY s.id, s.name
        HAVING AVG(g.grade) < 4.0
        FOR UPDATE OF s;
    student_rec RECORD;
    updated_count INT := 0;
BEGIN
    -- Добавляем колонку, если её нет
    BEGIN
        ALTER TABLE students ADD COLUMN IF NOT EXISTS attention_flag BOOLEAN DEFAULT FALSE;
    EXCEPTION WHEN duplicate_column THEN
        NULL;
    END;
    
    OPEN low_gpa_cursor;
    
    LOOP
        FETCH low_gpa_cursor INTO student_rec;
        EXIT WHEN NOT FOUND;
        
        UPDATE students 
        SET attention_flag = TRUE
        WHERE id = student_rec.id;
        
        RAISE NOTICE 'Marked student: % (GPA: %)', student_rec.name, ROUND(student_rec.avg_grade::numeric, 2);
        updated_count := updated_count + 1;
    END LOOP;
    
    CLOSE low_gpa_cursor;
    RAISE NOTICE 'Total marked: % students', updated_count;
END $$;
