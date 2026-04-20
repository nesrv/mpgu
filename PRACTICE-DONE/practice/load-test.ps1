# PowerShell аналог Apache Benchmark (ab)
param(
    [string]$url,
    [int]$requests = 100,
    [int]$concurrent = 10
)

if (-not $url) {
    Write-Host "Использование: .\load-test.ps1 -url http://example.com [-requests 100] [-concurrent 10]"
    exit 1
}

Write-Host "Запуск нагрузочного тестирования..."
Write-Host "URL: $url"
Write-Host "Запросов: $requests"
Write-Host "Одновременно: $concurrent"

$startTime = Get-Date

# Запуск параллельных запросов
$jobs = @()
for ($i = 0; $i -lt $concurrent; $i++) {
    $job = Start-Job -ScriptBlock {
        param($url, $requestsPerJob)
        $results = @()
        for ($j = 0; $j -lt $requestsPerJob; $j++) {
            $start = Get-Date
            try {
                $response = Invoke-WebRequest -Uri $url -UseBasicParsing
                $end = Get-Date
                $results += @{
                    Status = $response.StatusCode
                    Time = ($end - $start).TotalMilliseconds
                }
            } catch {
                $end = Get-Date
                $results += @{
                    Status = "Error"
                    Time = ($end - $start).TotalMilliseconds
                }
            }
        }
        return $results
    } -ArgumentList $url, [math]::Floor($requests / $concurrent)
    
    $jobs += $job
}

# Ожидание завершения
$allResults = @()
foreach ($job in $jobs) {
    $result = Receive-Job -Job $job -Wait
    $allResults += $result
    Remove-Job -Job $job
}

$endTime = Get-Date
$totalTime = ($endTime - $startTime).TotalSeconds

# Статистика
$successCount = ($allResults | Where-Object { $_.Status -eq 200 }).Count
$avgTime = ($allResults | Measure-Object -Property Time -Average).Average

Write-Host "`nРезультаты:"
Write-Host "Общее время: $totalTime сек"
Write-Host "Успешных запросов: $successCount из $($allResults.Count)"
Write-Host "Среднее время ответа: $([math]::Round($avgTime, 2)) мс"
Write-Host "Запросов в секунду: $([math]::Round($allResults.Count / $totalTime, 2))"