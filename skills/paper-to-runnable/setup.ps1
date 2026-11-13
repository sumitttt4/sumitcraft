# Windows wrapper for setup.py. Shows the plan; add --yes to install.
#   powershell -ExecutionPolicy Bypass -File setup.ps1 [--yes] [--extra NAME]
$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) { & py -3 "$PSScriptRoot\setup.py" @args } else { & python "$PSScriptRoot\setup.py" @args }
exit $LASTEXITCODE
