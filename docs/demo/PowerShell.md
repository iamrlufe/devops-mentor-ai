# PowerShell

PowerShell — оболочка и язык сценариев, где команды возвращают объекты,
а не текст. Это позволяет передавать результат по конвейеру без разбора строк.

## Основы

```powershell
Get-Process | Where-Object { $_.CPU -gt 10 } | Sort-Object CPU -Descending
```

Команды называются по схеме «Глагол-Существительное»: `Get-Service`,
`Set-Location`, `New-Item`, `Remove-Item`.

## Работа с сервисами

```powershell
Get-Service -Name Spooler
Restart-Service -Name Spooler
```

## Практика

`Get-Member` показывает свойства и методы объекта — это основной способ понять,
с чем вы работаете:

```powershell
Get-Process | Get-Member
```

Для планирования задач применяют `Register-ScheduledJob`, для удалённого
выполнения — `Invoke-Command -ComputerName`.
