@echo off
REM Простой аналог Apache Benchmark с использованием curl
if "%1"=="" (
    echo Использование: simple-benchmark.bat URL [количество_запросов]
    echo Пример: simple-benchmark.bat http://example.com 100
    exit /b 1
)

set URL=%1
set REQUESTS=%2
if "%REQUESTS%"=="" set REQUESTS=10

echo Тестирование %URL% с %REQUESTS% запросами...
echo.

for /L %%i in (1,1,%REQUESTS%) do (
    curl -s -w "Запрос %%i: %%{http_code} - %%{time_total}s\n" -o nul %URL%
)

echo.
echo Тестирование завершено!