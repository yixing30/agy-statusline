# PowerShell Installer for Antigravity Modern Statusline
# Usage: powershell -ExecutionPolicy Bypass -File .\install.ps1

$ErrorActionPreference = "Stop"

Write-Host "`n=== Antigravity Modern Statusline Installer ===" -ForegroundColor Cyan

# 1. Verify Python 3
Write-Host "[1/4] Checking Python 3..." -ForegroundColor Yellow
try {
    $pyVersion = python --version 2>&1
    Write-Host "      Found: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "      [!] Python 3 was not found in PATH. Please install Python 3.8+." -ForegroundColor Red
    exit 1
}

# 2. Prepare Target Directory (~/.gemini)
$geminiDir = Join-Path $HOME ".gemini"
Write-Host "[2/4] Target directory: $geminiDir" -ForegroundColor Yellow
if (-not (Test-Path $geminiDir)) {
    New-Item -ItemType Directory -Path $geminiDir -Force | Out-Null
}

# 3. Copy Files
Write-Host "[3/4] Installing statusline scripts..." -ForegroundColor Yellow
$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = (Get-Location).Path }

$destScript = Join-Path $geminiDir "statusline.py"
$destConfig = Join-Path $geminiDir "statusline.config.json"

Copy-Item -Path (Join-Path $scriptDir "statusline.py") -Destination $destScript -Force
Write-Host "      Installed: $destScript" -ForegroundColor Green

if (-not (Test-Path $destConfig)) {
    Copy-Item -Path (Join-Path $scriptDir "statusline.config.json") -Destination $destConfig -Force
    Write-Host "      Installed default config: $destConfig" -ForegroundColor Green
} else {
    Write-Host "      Existing config preserved: $destConfig" -ForegroundColor Cyan
}

# 4. Settings Configuration instructions
Write-Host "[4/4] Configuring Antigravity CLI..." -ForegroundColor Yellow

$settingsPath = Join-Path $geminiDir "antigravity-cli\settings.json"
$expectedCommand = "python `"$destScript`""

$configured = $false
if (Test-Path $settingsPath) {
    try {
        $json = Get-Content $settingsPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if (-not $json.statusLine) {
            $json | Add-Member -MemberType NoteProperty -Name "statusLine" -Value $expectedCommand
        } else {
            $json.statusLine = $expectedCommand
        }
        $json | ConvertTo-Json -Depth 10 | Set-Content $settingsPath -Encoding UTF8
        Write-Host "      Updated: $settingsPath" -ForegroundColor Green
        $configured = $true
    } catch {
        Write-Host "      Could not automatically edit settings.json (permission restricted)." -ForegroundColor DarkGray
    }
}

Write-Host "`n=== Installation Complete! ===" -ForegroundColor Green
if (-not $configured) {
    Write-Host "`nTo activate in Antigravity CLI, make sure your ~/.gemini/antigravity-cli/settings.json includes:" -ForegroundColor Cyan
    Write-Host @"
{
  "statusLine": "python \"$destScript\""
}
"@ -ForegroundColor Yellow
}
Write-Host "`nRun 'agy' in any directory to experience your new statusline!`n" -ForegroundColor Cyan
