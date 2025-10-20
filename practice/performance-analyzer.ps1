param([string]$url, [int]$requests = 100)

if (-not $url) { Write-Host "Usage: .\performance-analyzer.ps1 -url http://example.com [-requests 100]"; exit 1 }

$results = @()
$startTime = Get-Date
Write-Host "Testing $url with $requests requests..."

for ($i = 0; $i -lt $requests; $i++) {
    $start = Get-Date
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing
        $end = Get-Date
        $results += @{
            Time = ($end - $start).TotalMilliseconds
            Size = $response.Content.Length
            Status = $response.StatusCode
        }
    } catch {
        $results += @{ Time = 0; Size = 0; Status = "Error" }
    }
    if ($i % 50 -eq 0) { Write-Host "Completed $i requests..." }
}

$endTime = Get-Date
$totalTime = ($endTime - $startTime).TotalSeconds
$successful = $results | Where-Object { $_.Status -eq 200 }
$times = $successful | ForEach-Object { $_.Time }
$sizes = $successful | ForEach-Object { $_.Size }

if ($times.Count -eq 0) { Write-Host "No successful requests"; exit 1 }

$sortedTimes = $times | Sort-Object
$totalBytes = ($sizes | Measure-Object -Sum).Sum

Write-Host "`n=== PERFORMANCE ANALYSIS ==="
Write-Host "Requests per second: $([math]::Round($successful.Count / $totalTime, 2))"
Write-Host "Time per request: $([math]::Round(($times | Measure-Object -Average).Average, 2)) ms"
Write-Host "Transfer rate: $([math]::Round($totalBytes / $totalTime / 1024, 2)) KB/sec"
Write-Host "`nPercentiles (ms):"
Write-Host "  50%: $([math]::Round($sortedTimes[[math]::Floor($sortedTimes.Count * 0.5)], 2))"
Write-Host "  90%: $([math]::Round($sortedTimes[[math]::Floor($sortedTimes.Count * 0.9)], 2))"
Write-Host "  95%: $([math]::Round($sortedTimes[[math]::Floor($sortedTimes.Count * 0.95)], 2))"
Write-Host "  99%: $([math]::Round($sortedTimes[[math]::Floor($sortedTimes.Count * 0.99)], 2))"