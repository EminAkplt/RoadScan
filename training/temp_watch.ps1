$log = "C:\Users\Emin\Desktop\RoadScan\training\temp_watch.log"
"=== Isi bekcisi basladi: $((Get-Date).ToString('HH:mm:ss')) ===" | Out-File $log -Append -Encoding utf8
$hot = 0; $maxT = 0
while ($true) {
  $py = Get-Process python -ErrorAction SilentlyContinue
  if (-not $py) { "$(Get-Date -f HH:mm:ss)  egitim bitti/yok -> izleme durdu (max gorulen: ${maxT}C)" | Out-File $log -Append -Encoding utf8; break }
  $line = (& "C:\Windows\System32\nvidia-smi.exe" --query-gpu=temperature.gpu,power.draw,utilization.gpu --format=csv,noheader 2>$null | Select-Object -First 1)
  $t = 0; try { $t = [int]( ($line -split ',')[0].Trim() ) } catch {}
  if ($t -gt $maxT) { $maxT = $t }
  "$(Get-Date -f HH:mm:ss)  ${t}C  $line" | Out-File $log -Append -Encoding utf8
  if ($t -ge 93) { $hot++ } else { $hot = 0 }
  if ($hot -ge 3) {
    "$(Get-Date -f HH:mm:ss)  !!! 93C+ surekli -> GUVENLIK: egitim durduruluyor" | Out-File $log -Append -Encoding utf8
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    break
  }
  Start-Sleep -Seconds 60
}
