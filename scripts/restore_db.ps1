# ==============================================================================
# Database Restore Script for Windows PowerShell (BDS Smart)
# ==============================================================================
param(
    [Parameter(Mandatory=$true)]
    [string]$BackupFile,
    [string]$DbContainer = "bds_postgres",
    [string]$DbUser = "postgres",
    [string]$DbName = "real_estate_db"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $BackupFile)) {
    Write-Error "Backup file [$BackupFile] not found!"
    exit 1
}

Write-Host "==========================================================" -ForegroundColor Red
Write-Host "WARNING: Restoring will overwrite existing data in [$DbName]!" -ForegroundColor Red
Write-Host "Restoring from: $BackupFile" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Red

$dockerRunning = docker ps --format "{{.Names}}" | Select-String "^$DbContainer$"
if ($dockerRunning) {
    Write-Host "Restoring into docker container [$DbContainer]..." -ForegroundColor Green
    Get-Content $BackupFile | docker exec -i $DbContainer psql -U $DbUser -d $DbName
} else {
    Write-Host "Restoring into local PostgreSQL..." -ForegroundColor Yellow
    Get-Content $BackupFile | psql -U $DbUser -d $DbName
}

Write-Host "Database restoration completed successfully!" -ForegroundColor Green
