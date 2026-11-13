# Windows wrapper for the SumitCraft doctor. Read-only: it changes nothing.
#   powershell -ExecutionPolicy Bypass -File tools\doctor.ps1 [--json] [--no-browser]
$os = Get-CimInstance Win32_OperatingSystem -ErrorAction SilentlyContinue
if ($os) { Write-Host ("Windows: {0} {1} (build {2})" -f $os.Caption, $os.Version, $os.BuildNumber) }
Write-Host ("PowerShell: {0}" -f $PSVersionTable.PSVersion)
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  Write-Host "Node.js: not found. Next step: winget install OpenJS.NodeJS.LTS   (then open a new terminal and run this again)"
  exit 1
}
& node "$PSScriptRoot\doctor.mjs" @args
exit $LASTEXITCODE
