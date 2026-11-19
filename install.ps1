#!/usr/bin/env pwsh
# install.ps1 — inventor-mcp for DSH
# 1) 检查 Python 3.12+；2) 安装 inventor-mcp-server 与 pywin32；
# 3) 把 cordis.patch.yml 里的 `command: 'python'` 换成检测到的解释器绝对路径。
# 用法：  .\install.ps1            （装到当前 Python 环境）
#         .\install.ps1 -PathOnly （只改配置，不装依赖）

[CmdletBinding()]
param(
    [switch]$PathOnly,
    [string]$Python = ""
)

$ErrorActionPreference = "Stop"
$here = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Definition }
$patch = Join-Path $here "cordis.patch.yml"

function Find-Python {
    param([string]$hint)
    $candidates = @()
    if ($hint) { $candidates += $hint }
    $candidates += @(
        (Get-Command python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source),
        (Get-Command python3 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source),
        "C:\Python314\python.exe",
        "C:\Python313\python.exe",
        "C:\Python312\python.exe"
    )
    foreach ($c in $candidates) {
        if (-not $c) { continue }
        if (-not (Test-Path $c)) { continue }
        $v = & $c -c "import sys;print('%d.%d' % sys.version_info[:2])" 2>$null
        if ($LASTEXITCODE -eq 0 -and $v) {
            $parts = $v.Trim().Split('.')
            if ([int]$parts[0] -eq 3 -and [int]$parts[1] -ge 12) {
                return @{ Exe = $c; Version = $v.Trim() }
            }
        }
    }
    return $null
}

$py = Find-Python -hint $Python
if (-not $py) {
    Write-Host "[x] 没找到 Python 3.12+" -ForegroundColor Red
    Write-Host "    请安装 Python 3.12/3.13/3.14 后重试，或用 -Python 指定完整路径："
    Write-Host "    .\install.ps1 -Python 'C:\Python314\python.exe'"
    exit 1
}
Write-Host "[+] Python $($py.Version) -> $($py.Exe)" -ForegroundColor Green

if (-not $PathOnly) {
    Write-Host "[*] pip install inventor-mcp-server pywin32 ..."
    & $py.Exe -m pip install --upgrade inventor-mcp-server pywin32
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[x] pip 安装失败。请检查网络/代理，或手动执行：" -ForegroundColor Red
        Write-Host "    $($py.Exe) -m pip install --upgrade inventor-mcp-server pywin32"
        exit 2
    }
    & $py.Exe -c "import inventor_mcp_server.server as s; print('[+] inventor-mcp-server OK:', s.__file__)"
    if ($LASTEXITCODE -ne 0) { Write-Host "[x] 安装后仍无法 import，请检查 pip 输出" -ForegroundColor Red; exit 3 }
}

# 把 command 行替换为绝对路径（保持 YAML 其余不变）
if (-not (Test-Path $patch)) {
    Write-Host "[x] 找不到 cordis.patch.yml" -ForegroundColor Red; exit 4
}
$yaml = Get-Content -Path $patch -Raw -Encoding UTF8
$newYaml = [regex]::Replace($yaml, "(?m)^\s*command:\s*'python'\s*$", "        command: '$($py.Exe.Replace("'", "''"))'")
# 同时把启动器脚本的绝对路径重写成本仓库位置（args 里的 run_inventor_mcp.py）
$launcher = Join-Path $here "run_inventor_mcp.py"
$newYaml = [regex]::Replace($newYaml, "(?m)^(\s*)-\s*'.*run_inventor_mcp\.py'\s*$", "`$1- '$($launcher.Replace("'", "''"))'")
if ($newYaml -ne $yaml) {
    Set-Content -Path $patch -Value $newYaml -Encoding UTF8 -NoNewline
    Write-Host "[+] cordis.patch.yml: command -> $($py.Exe)" -ForegroundColor Green
} else {
    Write-Host "[i] cordis.patch.yml 的 command 已是绝对路径或未匹配，跳过"
}

Write-Host ""
Write-Host "下一步：把本目录注册到 DSH ——" -ForegroundColor Cyan
Write-Host "  在 DSH 会话里执行：plugin_manager install_bundle $here"
Write-Host "  然后：connect()"
