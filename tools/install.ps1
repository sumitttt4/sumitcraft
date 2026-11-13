# Windows wrapper: node tools\install.mjs with the same arguments. Nothing touches your global skills folder without --yes.
#   powershell -ExecutionPolicy Bypass -File tools\install.ps1 install code-loop design-critique --scope project
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { Write-Error "Node.js 18.19+ is needed: winget install OpenJS.NodeJS.LTS"; exit 1 }
& node "$PSScriptRoot\install.mjs" @args
exit $LASTEXITCODE
