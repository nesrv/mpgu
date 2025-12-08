# Простой нагрузочный тест для Windows PowerShell
$url = "http://localhost:8000/hit"
$requests = 100
$concurrent = 10

Write-Host "Запуск нагрузочного теста: $requests запросов, $concurrent потоков"
$start = Get-Date

$jobs = @()
for ($i = 0; $i -lt $concurrent; $i++) {
    $job = Start-Job -ScriptBlock {
        param($url, $count)
        for ($j = 0; $j -lt $count; $j++) {
            try {
                Invoke-WebRequest -Uri $url -Method POST -UseBasicParsing | Out-Null
            } catch {
                Write-Host "Ошибка: $_"
            }
        }
    } -ArgumentList $url, ($requests / $concurrent)
    $jobs += $job
}

# Ждем завершения всех задач
$jobs | Wait-Job | Out-Null
$jobs | Remove-Job

$end = Get-Date
$duration = ($end - $start).TotalSeconds

Write-Host "Завершено за $duration секунд"
Write-Host "Скорость: $([math]::Round($requests / $duration, 2)) запросов/сек"