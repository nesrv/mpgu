# PowerShell аналог htpasswd
param(
    [string]$username,
    [string]$password,
    [string]$file = ".htpasswd"
)

if (-not $username -or -not $password) {
    Write-Host "Использование: .\htpasswd-alternative.ps1 -username user -password pass [-file .htpasswd]"
    exit 1
}

# Генерация MD5 хеша (Apache MD5)
$salt = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 8 | % {[char]$_})
$hash = [System.Web.Security.FormsAuthentication]::HashPasswordForStoringInConfigFile($password + $salt, "MD5")
$entry = "$username`:`$apr1`$$salt`$$hash"

# Добавление в файл
Add-Content -Path $file -Value $entry
Write-Host "Пользователь $username добавлен в $file"