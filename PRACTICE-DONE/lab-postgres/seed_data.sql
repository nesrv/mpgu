-- SQL скрипт для создания таблиц и наполнения тестовыми данными

-- Удаление таблиц, если они существуют (в обратном порядке из-за внешних ключей)
DROP TABLE IF EXISTS grades CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS courses CASCADE;

-- Создание таблицы студентов
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы курсов
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    credits INTEGER DEFAULT 3
);

-- Создание таблицы оценок
CREATE TABLE grades (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    grade REAL NOT NULL
);

-- Создание индексов для улучшения производительности
CREATE INDEX idx_students_email ON students(email);
CREATE INDEX idx_grades_student_id ON grades(student_id);
CREATE INDEX idx_grades_course_id ON grades(course_id);

-- Вставка студентов
INSERT INTO students (name, email, status, created_at) VALUES
('Иван Иванов', 'ivan.ivanov@example.com', 'active', NOW()),
('Мария Петрова', 'maria.petrova@example.com', 'active', NOW()),
('Алексей Сидоров', 'alexey.sidorov@example.com', 'active', NOW()),
('Елена Козлова', 'elena.kozlova@example.com', 'inactive', NOW()),
('Дмитрий Волков', 'dmitry.volkov@example.com', 'active', NOW()),
('Анна Смирнова', 'anna.smirnova@example.com', 'active', NOW()),
('Сергей Лебедев', 'sergey.lebedev@example.com', 'active', NOW()),
('Ольга Новикова', 'olga.novikova@example.com', 'inactive', NOW());

-- Вставка курсов
INSERT INTO courses (title, credits) VALUES
('Математика', 4),
('Физика', 3),
('Программирование', 5),
('Базы данных', 4),
('Алгоритмы и структуры данных', 4),
('Веб-разработка', 3);

-- Вставка оценок
INSERT INTO grades (student_id, course_id, grade) VALUES
-- Иван Иванов (id=1)
(1, 1, 5.0),  -- Математика
(1, 2, 4.5),  -- Физика
(1, 3, 5.0),  -- Программирование
(1, 4, 4.0),  -- Базы данных

-- Мария Петрова (id=2)
(2, 1, 4.5),  -- Математика
(2, 3, 5.0),  -- Программирование
(2, 4, 5.0),  -- Базы данных
(2, 5, 4.5),  -- Алгоритмы

-- Алексей Сидоров (id=3)
(3, 2, 3.5),  -- Физика
(3, 3, 4.0),  -- Программирование
(3, 6, 4.5),  -- Веб-разработка

-- Елена Козлова (id=4) - неактивный студент
(4, 1, 3.0),  -- Математика
(4, 2, 3.5),  -- Физика

-- Дмитрий Волков (id=5)
(5, 1, 5.0),  -- Математика
(5, 2, 5.0),  -- Физика
(5, 3, 4.5),  -- Программирование
(5, 4, 5.0),  -- Базы данных
(5, 5, 5.0),  -- Алгоритмы
(5, 6, 4.5),  -- Веб-разработка

-- Анна Смирнова (id=6)
(6, 3, 4.0),  -- Программирование
(6, 4, 4.5),  -- Базы данных
(6, 6, 5.0),  -- Веб-разработка

-- Сергей Лебедев (id=7)
(7, 1, 4.0),  -- Математика
(7, 3, 4.5),  -- Программирование
(7, 5, 4.0),  -- Алгоритмы

-- Ольга Новикова (id=8) - неактивный студент
(8, 1, 3.5),  -- Математика
(8, 6, 3.0);  -- Веб-разработка

