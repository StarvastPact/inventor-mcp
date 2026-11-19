# install.ps1 - inventor-mcp for DSH
# 1) 检查 Python 3.12+   2) 安装 inventor-mcp-server 与 pywin32
# 3) 把 cordis.patch.yml 里的 python 和启动器路径改成绝对路径
#
# 用法:
#   .\install.ps1              安装依赖并改写配置
#   .\install.ps1 -PathOnly    只改写配置，不装依赖
#   .\install.ps1 -Python C:\Python314\python.exe
[CmdletBinding()]
param(
    [switch]$PathOnly,
    [string]$Python = ""
)

$ErrorActionPreference = "Continue"
$RepoRoot  = $PSScriptRoot
$PatchFile = Join-Path $RepoRoot "cordis.patch.yml"
$Launcher  = Join-Path $RepoRoot "run_inventor_mcp.py"

function Find-Python([string]$hint) {
    $candidates = @()
    if ($hint) { $candidates += $hint }
    foreach ($n in @("python", "python3")) {
        $cmd = Get-Command $n -ErrorAction SilentlyContinue
        if ($cmd) { $candidates += $cmd.Source }
    }
    foreach ($v in @("314", "313", "312")) {
        $candidates += ("C:\Python" + $v + "\python.exe")
    }
    foreach ($c in $candidates) {
        if (-not (Test-Path $c)) { continue }
        $ver = & $c -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null
        if (-not $ver) { continue }
        $parts = $ver.Trim().Split(".")
        if ([int]$parts[0] -eq 3 -and [int]$parts[1] -ge 12) {
            return [pscustomobject]@{ Exe = $c; Version = $ver.Trim() }
        }
    }
    return $null
}

$py = Find-Python -hint $Python
if (-not $py) {
    Write-Host "[x] 没找到 Python 3.12+" -ForegroundColor Red
    Write-Host "    请安装 Python 3.12/3.13/3.14，或用 -Python 指定完整路径:" -ForegroundColor Red
    Write-Host "    .\install.ps1 -Python 'C:\Python314\python.exe'" -ForegroundColor Red
    exit 1
}
Write-Host ("[+] Python " + $py.Version + " -> " + $py.Exe) -ForegroundColor Green

if (-not $PathOnly) {
    Write-Host "[*] pip install inventor-mcp-server pywin32 ..."
    & $py.Exe -m pip install --upgrade inventor-mcp-server pywin32
    if ($LASTEXITCODE -ne 0) {
        Write-Host ("[!] pip 安装失败(退出码 " + $LASTEXITCODE + ")。离线环境请改用 runtime 自包含方式。") -ForegroundColor Yellow
    } else {
        Write-Host "[+] 依赖安装完成" -ForegroundColor Green
    }
}

# --- 改写 cordis.patch.yml 里的绝对路径 ---
if (-not (Test-Path $PatchFile)) {
    Write-Host "[x] 找不到 cordis.patch.yml" -ForegroundColor Red
    exit 1
}
$yaml = Get-Content -Path $PatchFile -Raw -Encoding UTF8

$cmdPattern = "(?m)^(\s*)command:\s*'[^']*'(.*)$"
$cmdReplacement = '$1command: ' + [char]39 + '{0}' + [char]39 + '$2'
$newYaml = [regex]::Replace($yaml, $cmdPattern, [string]::Format($cmdReplacement, $py.Exe))

$argPattern = "(?m)^(\s*)-\s*'[^']*run_inventor_mcp\.py'\s*$"
$argReplacement = '$1- ' + [char]39 + '{0}' + [char]39
$newYaml = [regex]::Replace($newYaml, $argPattern, [string]::Format($argReplacement, $Launcher))

if ($newYaml -ne $yaml) {
    Set-Content -Path $PatchFile -Value $newYaml -Encoding UTF8 -NoNewline
    Write-Host ("[+] cordis.patch.yml: command -> " + $py.Exe) -ForegroundColor Green
    Write-Host ("[+] cordis.patch.yml: launcher -> " + $Launcher) -ForegroundColor Green
} else {
    Write-Host "[i] cordis.patch.yml 无需修改" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host ("下一步: 在 DSH 会话里执行 plugin_manager install_bundle " + $RepoRoot) -ForegroundColor Cyan
