
## Что такое MERGE?
`MERGE` (также известный как UPSERT) позволяет объединять данные - вставлять новые записи или обновлять существующие в одной операции.

## Синтаксис:
```sql
MERGE INTO target_table 
USING source_table 
ON condition
WHEN MATCHED THEN
    UPDATE SET column = value
WHEN NOT MATCHED THEN
    INSERT (columns) VALUES (values);
```


### Пример MERGE:
```sql
-- Обновляем или добавляем курсы для студента
MERGE INTO courses AS target
USING (VALUES (1, 'Математика', 95)) AS source(student_id, course_name, grade)
ON target.student_id = source.student_id AND target.course_name = source.course_name
WHEN MATCHED THEN
    UPDATE SET grade = source.grade
WHEN NOT MATCHED THEN
    INSERT (student_id, course_name, grade) 
    VALUES (source.student_id, source.course_name, source.grade);
```

### Более сложный пример:
```sql
-- Обновляем несколько курсов сразу
MERGE INTO courses
USING (VALUES 
    (1, 'Математика', 90),
    (1, 'Физика', 85),
    (2, 'Химия', 88)
) AS new_courses(student_id, course_name, grade)
ON courses.student_id = new_courses.student_id 
   AND courses.course_name = new_courses.course_name
WHEN MATCHED THEN
    UPDATE SET grade = new_courses.grade
WHEN NOT MATCHED THEN
    INSERT (student_id, course_name, grade)
    VALUES (new_courses.student_id, new_courses.course_name, new_courses.grade);
```

## Когда использовать:
- Синхронизация данных между таблицами
- Пакетное обновление записей
- Импорт данных с обработкой дубликатов
- Поддержание актуальности данных

MERGE заменяет громоздкие конструкции с проверкой `EXISTS` и отдельными `INSERT/UPDATE`.