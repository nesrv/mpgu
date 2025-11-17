import codecs

html_content = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Лабораторная работа: FastAPI - Маршрутизация и Архитектура</title>
    <style media="print">
        body { font-family: Arial, sans-serif; font-size: 12px; }
        .container { box-shadow: none; background: white; }
        .header { background: white !important; color: black !important; }
        .save-btn { display: none !important; }
        .section { page-break-inside: avoid; }
        input, textarea { border: 1px solid #ccc; background: white; color: black; }
        .code-block { background: white !important; color: black !important; border: 1px solid #ccc; }
    </style>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1200px; margin: 20px auto; padding: 20px; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .header { text-align: center; padding: 30px 0; background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%); color: white; border-radius: 10px; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .student-info { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; color: #4A90E2; }
        .form-group input, .form-group textarea { width: 100%; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 16px; transition: border-color 0.3s; }
        .form-group input:focus, .form-group textarea:focus { outline: none; border-color: #4A90E2; box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1); }
        .form-group textarea { min-height: auto; resize: vertical; }
        .section textarea.code-textarea { min-height: 300px; }
        .code-textarea { font-family: 'Courier New', monospace; background: #2d3748; color: #e2e8f0; white-space: pre; }
        .section { margin-bottom: 40px; padding: 25px; background: #fff; border-left: 5px solid #4A90E2; border-radius: 0 10px 10px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .section h2 { color: #4A90E2; margin-bottom: 20px; font-size: 1.8em; }
        .section h3 { color: #357ABD; margin: 20px 0 10px 0; font-size: 1.3em; }
        .code-block { background: #2d3748; color: #e2e8f0; padding: 20px; border-radius: 8px; margin: 15px 0; font-family: 'Courier New', monospace; overflow-x: auto; white-space: pre; }
        .checkbox-item { margin: 15px 0; padding: 15px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; display: flex; align-items: center; transition: transform 0.2s, box-shadow 0.2s; }
        .checkbox-item:hover { transform: translateX(5px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3); }
        .checkbox-item input[type="checkbox"] { appearance: none; width: 24px; height: 24px; border: 3px solid white; border-radius: 6px; margin-right: 15px; cursor: pointer; position: relative; background: transparent; transition: all 0.3s; }
        .checkbox-item input[type="checkbox"]:checked { background: white; }
        .checkbox-item input[type="checkbox"]:checked::after { content: '✓'; position: absolute; top: -2px; left: 4px; font-size: 18px; color: #667eea; font-weight: bold; }
        .checkbox-item label { color: white; font-weight: 500; cursor: pointer; user-select: none; }
        .save-btn { background: linear-gradient(135deg, #2ecc71, #27ae60); color: white; border: none; padding: 15px 30px; font-size: 18px; border-radius: 10px; cursor: pointer; display: block; margin: 30px auto; transition: transform 0.3s; }
        .save-btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(46, 204, 113, 0.3); }
        .info-box { background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 20px 0; border-radius: 5px; }
        ul { list-style: none; padding-left: 0; }
        ul li { padding: 8px 0 8px 30px; position: relative; }
        ul li::before { content: '▸'; position: absolute; left: 0; color: #4A90E2; font-size: 18px; font-weight: bold; }
        @media (max-width: 768px) { .student-info { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Лабораторная работа</h1>
            <h2>FastAPI - Маршрутизация, Архитектура, Dependency Injection</h2>
        </div>

        <div class="student-info">
            <div class="form-group">
                <label for="student-name">ФИО студента:</label>
                <input type="text" id="student-name" placeholder="Иванов Иван Иванович">
            </div>
            <div class="form-group">
                <label for="group">Группа:</label>
                <input type="text" id="group" placeholder="ИСТ-401">
            </div>
            <div class="form-group">
                <label for="date">Дата:</label>
                <input type="date" id="date">
            </div>
        </div>

        <div class="section">
            <h2>🎯 Цель работы</h2>
            <p>Изучить принципы построения масштабируемых API с использованием FastAPI, включая маршрутизацию, архитектурные паттерны и методы аутентификации.</p>
        </div>

        <div class="section">
            <h2>📋 Исходный код</h2>
            <p>Дан монолитный код в одном файле:</p>
            <div class="form-group">
                <textarea class="code-textarea" readonly># main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

class Student(BaseModel):
    name: str
    group: str
    year: int = Field(ge=1, le=5)

_students: list[Student] = []

@app.get("/students")
def get_all() -> list[Student]:
    return _students

@app.post("/students")
def create(student: Student) -> Student:
    _students.append(student)
    return student</textarea>
            </div>
        </div>

        <div class="section">
            <h2>📝 Задание 1: Маршрутизация с APIRouter</h2>
            <p>Разделить монолитный код на модули с использованием APIRouter.</p>
            
            <h3>Структура проекта:</h3>
            <div class="code-block">project-simple/
├── main.py      # FastAPI app + router подключение
├── models.py    # Student, StudentUpdate модели
└── students.py  # API endpoints + бизнес-логика</div>

            <div class="form-group">
                <label>Ваше решение:</label>
                <textarea class="code-textarea" placeholder="# Ваш код здесь..."></textarea>
            </div>

            <div class="checkbox-item">
                <input type="checkbox" id="task1-1">
                <label for="task1-1">Код разделен на модули</label>
            </div>
            <div class="checkbox-item">
                <input type="checkbox" id="task1-2">
                <label for="task1-2">APIRouter работает корректно</label>
            </div>
        </div>

        <div class="section">
            <h2>📝 Задание 2: Добавление модели Курсы</h2>
            <p>Создать модель Course и добавить CRUD операции.</p>
            
            <div class="info-box">
                <strong>Требования:</strong>
                <ul>
                    <li>Модель Course с полями: id, name, credits, semester</li>
                    <li>Добавить поле courses: list[int] в модель Student</li>
                    <li>Создать роутер courses.py с CRUD операциями</li>
                </ul>
            </div>

            <div class="form-group">
                <label>Ваше решение:</label>
                <textarea class="code-textarea" placeholder="# Ваш код здесь..."></textarea>
            </div>

            <div class="checkbox-item">
                <input type="checkbox" id="task2-1">
                <label for="task2-1">Модель Course создана</label>
            </div>
            <div class="checkbox-item">
                <input type="checkbox" id="task2-2">
                <label for="task2-2">CRUD операции реализованы</label>
            </div>
        </div>

        <div class="section">
            <h2>📝 Задание 3: Сложная архитектура (Repository + Service)</h2>
            <p>Разделить слои по зонам ответственности.</p>
            
            <h3>Структура проекта:</h3>
            <div class="code-block">project-pattern/
├── main.py
├── api/                   # REST эндпоинты
├── services/              # Бизнес-логика
├── repositories/          # Работа с данными
├── models/                # Доменные модели
└── schemas/               # Валидация API</div>

            <div class="form-group">
                <label>Ваше решение:</label>
                <textarea class="code-textarea" placeholder="# Ваш код здесь..."></textarea>
            </div>

            <div class="checkbox-item">
                <input type="checkbox" id="task3-1">
                <label for="task3-1">Архитектура реализована</label>
            </div>
        </div>

        <div class="section">
            <h2>🐘 Задание 4: Подключение PostgreSQL</h2>
            <p>Заменить in-memory хранилище на PostgreSQL в Docker контейнере.</p>
            
            <h3>Dockerfile:</h3>
            <div class="code-block">FROM postgres:18

ENV POSTGRES_DB=students_db
ENV POSTGRES_USER=student
ENV POSTGRES_PASSWORD=password

EXPOSE 5432</div>

            <h3>Команды запуска:</h3>
            <div class="code-block">docker build -t postgres-students .
docker run -d -p 5432:5432 postgres-students</div>

            <div class="form-group">
                <label>Ваше решение database.py:</label>
                <textarea class="code-textarea" placeholder="# Ваш код здесь..."></textarea>
            </div>

            <div class="checkbox-item">
                <input type="checkbox" id="task4-1">
                <label for="task4-1">PostgreSQL запущен</label>
            </div>
            <div class="checkbox-item">
                <input type="checkbox" id="task4-2">
                <label for="task4-2">SQLAlchemy настроен</label>
            </div>
        </div>

        <div class="section">
            <h2>📝 Задание 5: Dependency Injection</h2>
            <p>Реализовать паттерн Dependency Injection для работы с базой данных.</p>
            
            <div class="form-group">
                <label>Ваше решение:</label>
                <textarea class="code-textarea" placeholder="# Ваш код здесь..."></textarea>
            </div>

            <div class="checkbox-item">
                <input type="checkbox" id="task5-1">
                <label for="task5-1">DI реализован</label>
            </div>
        </div>

        <div class="section">
            <h2>📊 Выводы</h2>
            <div class="form-group">
                <label>Что изучили:</label>
                <textarea rows="3" placeholder="Опишите основные темы..."></textarea>
            </div>
            <div class="form-group">
                <label>Трудности:</label>
                <textarea rows="3" placeholder="Что было сложно..."></textarea>
            </div>
        </div>

        <button class="save-btn" onclick="window.print()">💾 Сохранить в PDF</button>
    </div>

    <script>
        function loadFromStorage() {
            document.getElementById('student-name').value = localStorage.getItem('student-name') || '';
            document.getElementById('group').value = localStorage.getItem('group') || '';
            document.getElementById('date').value = localStorage.getItem('date') || new Date().toISOString().split('T')[0];
            document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                if (localStorage.getItem(checkbox.id) === 'true') checkbox.checked = true;
            });
            document.querySelectorAll('textarea').forEach((textarea, index) => {
                const saved = localStorage.getItem('textarea-' + index);
                if (saved) textarea.value = saved;
            });
        }
        
        function saveToStorage() {
            localStorage.setItem('student-name', document.getElementById('student-name').value);
            localStorage.setItem('group', document.getElementById('group').value);
            localStorage.setItem('date', document.getElementById('date').value);
            document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                localStorage.setItem(checkbox.id, checkbox.checked);
            });
            document.querySelectorAll('textarea').forEach((textarea, index) => {
                localStorage.setItem('textarea-' + index, textarea.value);
            });
        }
        
        loadFromStorage();
        document.getElementById('student-name').addEventListener('input', saveToStorage);
        document.getElementById('group').addEventListener('input', saveToStorage);
        document.getElementById('date').addEventListener('change', saveToStorage);
        document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', saveToStorage);
        });
        document.querySelectorAll('textarea').forEach(textarea => {
            textarea.addEventListener('input', saveToStorage);
        });
    </script>
</body>
</html>"""

with codecs.open('Веб_методичка_Архитектура_FastAPI.html', 'w', 'utf-8') as f:
    f.write(html_content)

print("HTML файл создан успешно!")
