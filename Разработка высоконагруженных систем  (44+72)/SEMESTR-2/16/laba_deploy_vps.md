# Методичка: от "Привет, мир" до FastAPI с GitHub

**Домен:** alekseeva.h1n.ru  
**Сервер:** 81.90.182.174  
**Студент:** Алексеева

---





## Содержание

1. [Часть 1: Простой сайт "Привет, мир"](#часть-1-простой-сайт-привет-мир)
2. [Часть 1a: Практика работы с Neovim](#часть-1a-практика-работы-с-neovim)
3. [Часть 2: FastAPI приложение](#часть-2-fastapi-приложение)
4. [Часть 3: Подключение GitHub репозитория](#часть-3-подключение-github-репозитория)
5. [Часть 4: Автоматический деплой (CI/CD)](#часть-4-автоматический-деплой-cicd)

---

## Часть 1: Простой сайт "Привет, мир"

> **Важно (вариант «студент всё делает сам»):** Во всех командах замените `alekseeva` на ваш логин. Команды для `/etc`, `/var/www`, `/opt` и `systemctl` выполняйте через `sudo` (преподаватель выдаёт пользователя с sudo).

> **Примечание:** Эта часть — учебный этап. В Части 2 мы заменим статический сайт на FastAPI приложение.

### 1.1. Подключение к серверу по SSH

Откройте терминал (PowerShell на Windows или Terminal на Mac/Linux):

```bash
# Если преподаватель выдал вам отдельного пользователя:
ssh alekseeva@81.90.182.174

# Или по root (если так настроено):
ssh root@81.90.182.174
```

Введите пароль, который вам дал преподаватель. Логин и пароль уточните у преподавателя.

---

### 1.2. Создание папки для вашего сайта

```bash
# Создаём папку (sudo — права на /var/www)
sudo mkdir -p /var/www/alekseeva
sudo chown $USER:$USER /var/www/alekseeva
cd /var/www/alekseeva
```

---

### 1.3. Создание HTML-страницы

```bash
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Сайт Алексеевой</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
            padding: 40px;
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        h1 { font-size: 3em; margin-bottom: 10px; }
        p { font-size: 1.2em; opacity: 0.9; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Привет, мир!</h1>
        <p>Это мой первый сайт на сервере</p>
        <p>Автор: Алексеева Анастасия</p>
    </div>
</body>
</html>
EOF
```

---

### 1.4. Настройка Nginx для вашего домена

Nginx использует схему **sites-available** / **sites-enabled**:
- `sites-available` — все заготовки конфигов (могут быть выключены),
- `sites-enabled` — только те, что активны (симлинки на файлы из sites-available).

В конфиге задаётся:
- **listen 80** — слушать порт 80 (HTTP),
- **server_name** — по какому домену Nginx будет отвечать,
- **root** — каталог с файлами сайта,
- **index** — файл по умолчанию при заходе в каталог,
- **try_files** — искать файл по URI, при отсутствии — 404.

Команда **ln -sf** создаёт символическую ссылку: «включить» конфиг, не удаляя оригинал. Перед перезагрузкой обязательно проверяем конфиг командой **nginx -t**, чтобы не сломать работающий Nginx.

```bash
# Создаём конфиг Nginx (sudo — запись в /etc)
cat << 'EOF' | sudo tee /etc/nginx/sites-available/alekseeva > /dev/null
server {
    listen 80;
    server_name alekseeva.h1n.ru;
    
    root /var/www/alekseeva;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
}
EOF

# Включаем сайт
sudo ln -sf /etc/nginx/sites-available/alekseeva /etc/nginx/sites-enabled/

# Проверяем конфигурацию и перезагружаем Nginx
sudo nginx -t && sudo systemctl reload nginx
```

**systemctl reload nginx** применяет новый конфиг без полной остановки сервиса — текущие соединения не обрываются, а новые запросы уже идут по новым правилам.

---

### 1.5. Проверка

Откройте в браузере: **http://alekseeva.h1n.ru**

Вы должны увидеть страницу "Привет, мир!".

---

## Часть 1a: Практика работы с Neovim

> **Цель:** установить Neovim на VPS и освоить базовые приёмы работы для редактирования конфигов и логов.

### 1a.1. Установка Neovim на VPS

Подключитесь к серверу по SSH (если ещё не подключены) и установите Neovim:

```bash
# Обновляем список пакетов (Ubuntu/Debian)
sudo apt update
sudo apt install -y neovim

# Проверяем установку
nvim --version
```

---

### 1a.2. Встроенный туториал (≈5 мин)

Запустите Neovim и откройте интерактивный туториал:

```bash
nvim
```

В окне Neovim наберите двоеточие и команду (в нижней строке появится курсор):

```
:Tutor
```

Нажмите Enter. Откроется встроенный туториал **на английском** — это нормально.

**Как открыть туториал на русском:**

Neovim по умолчанию показывает туториал на английском. Русский туториал поставляется с пакетом **vim-runtime**:

```bash
sudo apt install -y vim-runtime
```

Затем откройте русский туториал в Neovim:

```bash
# Путь зависит от версии (vim82, vim90 и т.д.)
nvim /usr/share/vim/vim*/tutor/tutor.ru
```

Или используйте **Vim** (он откроет тот же туториал):

```bash
sudo apt install -y vim
vimtutor ru
```

Если `tutor.ru` не найден — работайте с английской версией (`:Tutor`) по инструкциям выше; клавиши и команды одинаковые.

---

### 1a.3. Редактирование файла (≈5 мин)

Создайте тестовый файл и отредактируйте его в Neovim:

```bash
# Создаём файл
touch /tmp/neovim-test.txt

# Открываем в Neovim
nvim /tmp/neovim-test.txt
```

**Выполните:**

| Действие | Команда / клавиша |
|----------|-------------------|
| Войти в режим ввода | `i` |
| Написать: «Привет из Neovim!» | ввести текст |
| Выйти из ввода | `Esc` |
| Сохранить и выйти | `:wq` Enter |

Проверьте содержимое:

```bash
cat /tmp/neovim-test.txt
```

---

### 1a.4. Редактирование конфига Nginx (≈5 мин)

Откройте конфиг вашего сайта в Neovim:

```bash
nvim /etc/nginx/sites-available/alekseeva
```

**Задание:**

1. С помощью `hjkl` или стрелок перейдите к строке `server_name`.
2. Нажмите `i` и добавьте пробел после `alekseeva.h1n.ru` (не меняя логику).
3. Или добавьте комментарий: нажмите `o` (новая строка снизу), введите `# Тестовый комментарий`.
4. **Не сохраняйте** изменения — наберите `:q!` Enter, чтобы выйти без сохранения (иначе можно сломать конфиг).
5. Проверьте, что сайт по-прежнему работает: http://alekseeva.h1n.ru

---

### 1a.5. Просмотр логов (≈3 мин)

Откройте лог Nginx (если файл существует):

```bash
nvim /var/log/nginx/access.log
```

Потренируйтесь в навигации:

| Клавиша | Действие |
|---------|----------|
| `j` / `k` | вниз / вверх по строкам |
| `G` | в конец файла |
| `gg` | в начало файла |
| `:q!` | выйти без сохранения |

---

### 1a.6. Шпаргалка для деплоя

Минимальный набор для работы с конфигами на сервере:

| Задача | Действие |
|--------|----------|
| Открыть файл | `nvim путь/к/файлу` |
| Войти в редактирование | `i` |
| Выйти из редактирования | `Esc` |
| Сохранить и выйти | `:wq` Enter |
| Выйти без сохранения | `:q!` Enter |

После выполнения Части 1a вы сможете править конфиги и логи на VPS без графического редактора.

---

## Часть 2: FastAPI приложение

### 2.1. Создание проекта FastAPI

```bash
# Создаём папку для FastAPI (sudo — права на /opt)
sudo mkdir -p /opt/alekseeva-api
sudo chown $USER:$USER /opt/alekseeva-api
cd /opt/alekseeva-api

# Создаём виртуальное окружение Python
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install fastapi uvicorn
```

---

### 2.2. Создание файла main.py

```bash
cat > main.py << 'EOF'
from fastapi import FastAPI

# Создаём приложение
app = FastAPI(
    title="API Алексеевой",
    description="Мой первый API на FastAPI",
    version="1.0.0"
)

@app.get("/")
def home():
    """Главная страница"""
    return {"message": "Привет, мир!", "author": "Алексеева А.А."}

@app.get("/health")
def health():
    """Проверка работоспособности"""
    return {"status": "ok"}

@app.get("/about")
def about():
    """Информация об авторе"""
    return {
        "name": "Алексеева А.А.",
        "project": "Учебный проект FastAPI",
        "university": "..."
    }
EOF
```

---

### 2.3. Проверка работы (вручную)

```bash
cd /opt/alekseeva-api
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8010
```

Откройте: **http://81.90.182.174:8010/docs** — вы увидите Swagger UI.

Остановите: `Ctrl+C`

---

### 2.4. Настройка автозапуска (systemd)

```bash
# Создаём unit-файл (sudo — запись в /etc)
cat << 'EOF' | sudo tee /etc/systemd/system/alekseeva-api.service > /dev/null
[Unit]
Description=Alekseeva FastAPI App
After=network.target

[Service]
User=root
WorkingDirectory=/opt/alekseeva-api
ExecStart=/opt/alekseeva-api/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8010
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Активируем и запускаем (sudo)
sudo systemctl daemon-reload
sudo systemctl enable alekseeva-api
sudo systemctl start alekseeva-api
sudo systemctl status alekseeva-api
```

---

### 2.5. Настройка Nginx для FastAPI

Обновляем конфиг Nginx — все запросы идут на FastAPI:

```bash
# Создаём конфиг (sudo)
cat << 'EOF' | sudo tee /etc/nginx/sites-available/alekseeva > /dev/null
server {
    listen 80;
    server_name alekseeva.h1n.ru;
    
    # Все запросы идут на FastAPI
    location / {
        proxy_pass http://127.0.0.1:8010;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo nginx -t && sudo systemctl reload nginx
```

---

### 2.6. Проверка

- **Главная:** http://alekseeva.h1n.ru/ — JSON `{"message": "Привет, мир!"}`
- **Health:** http://alekseeva.h1n.ru/health — `{"status": "ok"}`
- **About:** http://alekseeva.h1n.ru/about — информация
- **Swagger:** http://alekseeva.h1n.ru/docs — документация API

---

## Часть 3: Подключение GitHub репозитория

### 3.1. Создание репозитория на GitHub

1. Зайдите на https://github.com
2. Нажмите **New repository**
3. Название: `alekseeva-api`
4. Выберите **Public** или **Private**
5. Нажмите **Create repository**

---

### 3.2. Создание файлов проекта локально

На вашем компьютере (не на сервере!) создайте папку проекта:

```
alekseeva-api/
├── main.py
├── requirements.txt
└── README.md
```

**main.py:**

```python
from fastapi import FastAPI

app = FastAPI(
    title="API Алексеевой",
    description="Мой первый API на FastAPI",
    version="1.0.0"
)

@app.get("/")
def home():
    return {"message": "Привет, мир!", "author": "Алексеева"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/about")
def about():
    return {
        "name": "Алексеева",
        "project": "Учебный проект FastAPI"
    }
```

**requirements.txt:**

```
fastapi
uvicorn
```

**README.md:**

```markdown
# API Алексеевой

Учебный проект на FastAPI.

## Запуск локально

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Эндпоинты

- `GET /` — главная
- `GET /health` — статус
- `GET /about` — информация
- `GET /docs` — Swagger документация
```

---

### 3.3. Загрузка на GitHub

```bash
cd alekseeva-api

git init
git add .
git commit -m "Initial commit: FastAPI app"
git branch -M main
git remote add origin https://github.com/ВАШ_ЛОГИН/alekseeva-api.git
git push -u origin main
```

---

### 3.4. Клонирование на сервер

#### SSH по ключу (подключение к VPS без пароля)

1. **Генерация ключа** на вашем компьютере:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_ed25519 -N ""
```

2. **Копирование на VPS.** Linux/macOS: `ssh-copy-id root@81.90.182.174`  
Windows: скопируйте `~/.ssh/id_ed25519.pub` и на сервере: `mkdir -p ~/.ssh`, `echo "ВАШ_ПУБЛИЧНЫЙ_КЛЮЧ" >> ~/.ssh/authorized_keys`, `chmod 700 ~/.ssh`, `chmod 600 ~/.ssh/authorized_keys`

3. **Проверка:** `ssh root@81.90.182.174` — вход без пароля.

#### GitHub по SSH (git clone/pull без пароля)

1. **Добавьте ключ в GitHub:** Settings → SSH and GPG keys → New SSH key, вставьте `~/.ssh/id_ed25519.pub`
2. **Локально:** `git remote add origin git@github.com:ВАШ_ЛОГИН/alekseeva-api.git` (или `git remote set-url origin git@...` если уже добавлен HTTPS)
3. **На VPS для git pull:**
   - Создайте Deploy key: `ssh-keygen -t ed25519 -f ~/.ssh/github_deploy -N ""`
   - GitHub → репозиторий → Settings → Deploy keys → Add, вставьте `cat ~/.ssh/github_deploy.pub`

#### Клонирование и запуск

На сервере:

```bash
cd /opt
rm -rf alekseeva-api  # удаляем старую версию

# HTTPS (пароль/токен) или SSH (если настроен Deploy key):
git clone https://github.com/ВАШ_ЛОГИН/alekseeva-api.git
# git clone git@github.com:ВАШ_ЛОГИН/alekseeva-api.git

cd alekseeva-api

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

sudo systemctl restart alekseeva-api
sudo systemctl status alekseeva-api
```

---

## Часть 4: Автоматический деплой (CI/CD)

### 4.1. Создание скрипта деплоя на сервере

```bash
cat > /opt/alekseeva-api/deploy.sh << 'EOF'
#!/bin/bash
cd /opt/alekseeva-api
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart alekseeva-api
echo "Deploy completed!"
EOF

chmod +x /opt/alekseeva-api/deploy.sh
```

---

### 4.2. GitHub Actions (автоматический деплой при push)

В репозитории создайте файл `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Server

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: 81.90.182.174
          username: root  # или логин студента (alekseeva), если подключение по своему юзеру
          password: ${{ secrets.SSH_PASSWORD }}
          script: |
            cd /opt/alekseeva-api
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            systemctl restart alekseeva-api
```

---

### 4.3. Настройка секретов в GitHub

1. Откройте репозиторий на GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Нажмите **New repository secret**
4. Добавьте:
   - Name: `SSH_PASSWORD`
   - Value: пароль от сервера (root или логин студента)

---

### 4.4. Проверка

1. Измените код в `main.py` на своём компьютере
2. Сделайте commit и push:

```bash
git add .
git commit -m "Update: new feature"
git push
```

3. Откройте **Actions** в GitHub — увидите процесс деплоя
4. После завершения проверьте: http://alekseeva.h1n.ru/

---

## Полезные команды

| Действие | Команда |
|----------|---------|
| Логи приложения | `sudo journalctl -u alekseeva-api -f` |
| Перезапуск | `sudo systemctl restart alekseeva-api` |
| Статус | `sudo systemctl status alekseeva-api` |
| Остановка | `sudo systemctl stop alekseeva-api` |
| Обновить код | `cd /opt/alekseeva-api && git pull` |

---

## Итог

После выполнения всех шагов у вас будет:

1. ✅ FastAPI приложение на http://alekseeva.h1n.ru/
2. ✅ Health check на http://alekseeva.h1n.ru/health
3. ✅ Swagger документация на http://alekseeva.h1n.ru/docs
4. ✅ Код в GitHub репозитории
5. ✅ Автоматический деплой при каждом push

---

## Для преподавателя: вариант «студент всё делает сам»

Преподаватель создаёт только учётную запись с sudo. Всё остальное (каталоги, Nginx, systemd, GitHub) студент настраивает сам по методичке.

### 1. Создание пользователя

Подключитесь к серверу как `root` и выполните (замените `alekseeva` на логин студента):

```bash
adduser alekseeva
usermod -aG sudo alekseeva
```

При `adduser` введите пароль. Остальные поля — по желанию (Enter).

### 2. Выдача данных студенту

Передайте студенту:
- **Логин:** `alekseeva`
- **Пароль:** введённый при `adduser`
- **Сервер:** `81.90.182.174`
- **Домен:** `alekseeva.h1n.ru` (если настроен wildcard `*.h1n.ru` или отдельная DNS-запись)

Студент подключается: `ssh alekseeva@81.90.182.174` и выполняет шаги по методичке, подставляя свой логин вместо `alekseeva` и используя `sudo` где нужно.

### 3. Массовое создание

```bash
for user in alekseeva zavyalova patrusheva pilyutik; do
  adduser --disabled-password --gecos "" $user
  echo "$user:$user" | chpasswd
  usermod -aG sudo $user
done
```

Пароль у каждого пользователя совпадает с логином (например, `alekseeva` / `alekseeva`).

### 4. Удаление пользователя

```bash
# Завершить все процессы пользователя (если залогинен)
sudo pkill -u alekseeva

# Удалить пользователя и домашний каталог
sudo userdel -r alekseeva
```

Опционально: удалите его конфиги Nginx и systemd, каталоги `/var/www/alekseeva`, `/opt/alekseeva-api`.

---

