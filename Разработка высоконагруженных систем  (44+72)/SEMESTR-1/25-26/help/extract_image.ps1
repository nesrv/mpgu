$html = Get-Content 'dev2_17_ext_fts_overview.html' -Raw
$html -match 'data:image/png;base64,([^"]+)' > $null
$base64 = $matches[1]
$bytes = [Convert]::FromBase64String($base64)
[IO.File]::WriteAllBytes("$PWD\img\page1.png", $bytes)
