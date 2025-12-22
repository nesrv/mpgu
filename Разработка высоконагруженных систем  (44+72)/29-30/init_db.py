#!/usr/bin/env python3
import subprocess
import time

print("🗄️  Запуск PostgreSQL...")
subprocess.run("docker-compose up -d postgres", shell=True)

print("⏳ Ожидание готовности...")
for _ in range(30):
    result = subprocess.run(
        "docker-compose exec -T postgres pg_isready -U postgres",
        shell=True, capture_output=True
    )
    if result.returncode == 0:
        break
    time.sleep(2)

print("📝 Выполнение SQL...")
subprocess.run(
    "docker-compose exec -T postgres psql -U postgres -d messenger_channel -f /docker-entrypoint-initdb.d/init.sql",
    shell=True
)

print("✨ Готово!")

