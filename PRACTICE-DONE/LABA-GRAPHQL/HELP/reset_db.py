#!/usr/bin/env python3
"""
Скрипт для пересоздания базы данных (удаляет все данные и создает заново)
Использование: python reset_db.py
"""

import subprocess
import time
import sys
from pathlib import Path

def run_command(command, check=True, capture_output=False):
    """Выполняет команду и возвращает результат"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка выполнения команды: {e}")
        sys.exit(1)

def wait_for_postgres(max_attempts=30):
    """Ожидает готовности PostgreSQL"""
    print("⏳ Ожидание готовности PostgreSQL...")
    for attempt in range(max_attempts):
        result = run_command(
            "docker-compose exec -T postgres pg_isready -U postgres",
            check=False,
            capture_output=True
        )
        if result.returncode == 0:
            print("✅ PostgreSQL готов!")
            return True
        print(f"   PostgreSQL еще не готов, ждем... (попытка {attempt + 1}/{max_attempts})")
        time.sleep(2)
    print("❌ PostgreSQL не запустился за отведенное время")
    return False

def main():
    script_dir = Path(__file__).parent
    sql_file = script_dir / "sql.sql"
    
    if not sql_file.exists():
        print(f"❌ Файл {sql_file} не найден!")
        sys.exit(1)
    
    print("🛑 Остановка и удаление контейнера...")
    run_command("docker-compose down -v", capture_output=True)
    
    print("🗄️  Запуск PostgreSQL контейнера...")
    run_command("docker-compose up -d postgres", capture_output=True)
    
    if not wait_for_postgres():
        sys.exit(1)
    
    print("📝 Выполнение SQL скрипта...")
    result = run_command(
        f"docker-compose exec -T postgres psql -U postgres -d messenger_channel -f /docker-entrypoint-initdb.d/init.sql",
        capture_output=True
    )
    
    if result.returncode == 0:
        print("✨ База данных пересоздана и наполнена данными!")
        print("📊 Подключение: postgresql://postgres:postgres@localhost:5432/messenger_channel")
    else:
        print("❌ Ошибка при выполнении SQL скрипта")
        sys.exit(1)

if __name__ == "__main__":
    main()

