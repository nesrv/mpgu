# PowerShell скрипт для конвертации HTML в PDF
$htmlPath = "c:\W25\МПГУ\my-subjects\Управление разработкой программного обеспечения  (44+72)\2\spec.html"
$pdfPath = "c:\W25\МПГУ\my-subjects\Управление разработкой программного обеспечения  (44+72)\2\spec.pdf"

# Используем Internet Explorer для конвертации
try {
    $ie = New-Object -ComObject InternetExplorer.Application
    $ie.Visible = $false
    $ie.Navigate2($htmlPath)
    
    # Ждем загрузки
    while ($ie.Busy) { Start-Sleep -Milliseconds 100 }
    Start-Sleep -Seconds 2
    
    # Печать в PDF
    $ie.ExecWB(6, 2, $pdfPath)
    $ie.Quit()
    
    Write-Host "PDF создан успешно: $pdfPath"
} catch {
    Write-Host "Ошибка при создании PDF: $($_.Exception.Message)"
}