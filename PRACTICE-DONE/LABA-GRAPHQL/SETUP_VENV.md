# Настройка виртуального окружения в WSL

**Важно:** Виртуальное окружение создается в Linux файловой системе (`~/.venvs/`), а не в директории проекта, чтобы избежать проблем с правами доступа.

## Быстрый старт

```bash
# 1. Установка uv (если нужно)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc

# 2. Создание виртуального окружения
uv venv ~/.venvs/laba-graphql

# 3. Активация и установка зависимостей
source ~/.venvs/laba-graphql/bin/activate
cd /mnt/c/W26/project/mpgu_practice/LABA-GRAPHQL
uv pip install -r requirements.txt
```

## Ежедневная работа

```bash
# Активация окружения и переход в проект
source ~/.venvs/laba-graphql/bin/activate
cd /mnt/c/W26/project/mpgu_practice/LABA-GRAPHQL

# Или одной командой
cd /mnt/c/W26/project/mpgu_practice/LABA-GRAPHQL && source ~/.venvs/laba-graphql/bin/activate
```

### Алиас для удобства

Добавьте в `~/.bashrc`:
```bash
alias activate-graphql='cd /mnt/c/W26/project/mpgu_practice/LABA-GRAPHQL && source ~/.venvs/laba-graphql/bin/activate'
```

Затем: `source ~/.bashrc` и используйте `activate-graphql`

## Основные команды

```bash
# Активация
source ~/.venvs/laba-graphql/bin/activate

# Деактивация
deactivate

# Установка пакета
uv pip install название-пакета

# Список пакетов
uv pip list
```

## Решение проблем

**"Operation not permitted"** - виртуальное окружение на Windows FS. Удалите `.venv` в проекте и создайте в `~/.venvs/`

**"uv: command not found"** - добавьте в PATH:
```bash
export PATH="$HOME/.cargo/bin:$PATH"
```

**"externally-managed-environment"** - активируйте виртуальное окружение перед установкой
