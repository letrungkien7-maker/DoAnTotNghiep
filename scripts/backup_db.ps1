# ==============================================================================
# Database Backup Script for Windows PowerShell (BDS Smart)
# ==============================================================================
param(
    [string]$BackupDir = ".\backups",
    [string]$DbContainer = "bds_postgres",
    [string]$DbUser = "postgres",
    [string]$DbName = "real_estate_db"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path $BackupDir "bds_backup_$timestamp.sql"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Starting PostgreSQL backup: $DbName at $(Get-Date)" -ForegroundColor Cyan
Write-Host "Target file: $backupFile" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$dockerRunning = docker ps --format "{{.Names}}" | Select-String "^$DbContainer$"
if ($dockerRunning) {
    Write-Host "Executing pg_dump via docker container [$DbContainer]..." -ForegroundColor Green
    docker exec -t $DbContainer pg_dump -U $DbUser -d $DbName --clean --if-exists | Out-File -FilePath $backupFile -Encoding utf8
} else {
    Write-Host "Executing local pg_dump..." -ForegroundColor Yellow
    pg_dump -U $DbUser -d $DbName --clean --if-exists | Out-File -FilePath $backupFile -Encoding utf8
}

$fileItem = Get-Item $backupFile
Write-Host "Backup completed successfully! Size: $([math]::Round($fileItem.Length / 1MB, 2)) MB" -ForegroundColor Green
