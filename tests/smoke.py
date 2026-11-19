# -*- coding: utf-8 -*-
"""冒烟测试：不需要 Inventor 也能跑，验证安装是否完整。

    python tests/smoke.py

检查：Python 版本、inventor_mcp_server 可导入、MCP stdio 握手返回 66 个工具、
cordis.patch.yml 与 package.json 结构正确、run_inventor_mcp.py 无硬编码个人路径。
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
fails = []


def check(name, ok, detail=""):
    print(("  OK   " if ok else "  FAIL ") + name + ((" — " + detail) if detail else ""))
    if not ok:
        fails.append(name)


print("== Python ==")
v = sys.version_info
check("Python >= 3.12", (v.major, v.minor) >= (3, 12), "%d.%d.%d" % v[:3])

print("== 模块 ==")
try:
    import inventor_mcp_server.server as srv  # noqa: F401
    check("import inventor_mcp_server.server", True, os.path.dirname(srv.__file__))
except Exception as e:
    check("import inventor_mcp_server.server", False, repr(e)[:120])

print("== MCP stdio 握手 ==")
try:
    proc = subprocess.Popen(
        [PY, "-m", "inventor_mcp_server.server"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env=dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1"),
    )
    try:
        init = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                           "clientInfo": {"name": "smoke", "version": "1.0"}}}
        proc.stdin.write((json.dumps(init) + "\n").encode())
        proc.stdin.flush()
        resp = json.loads(proc.stdout.readline().decode("utf-8", "replace"))
        check("initialize 有 result", "result" in resp)

        proc.stdin.write((json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized",
                                      "params": {}}) + "\n").encode())
        proc.stdin.flush()
        proc.stdin.write((json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list",
                                      "params": {}}) + "\n").encode())
        proc.stdin.flush()
        tools = json.loads(proc.stdout.readline().decode("utf-8", "replace"))
        names = [t["name"] for t in tools.get("result", {}).get("tools", [])]
        check("tools/list >= 60 个工具", len(names) >= 60, "%d 个" % len(names))
        for must in ("connect", "create_document", "create_sketch", "extrude", "capture_view"):
            check("工具存在: " + must, must in names)
    finally:
        proc.kill()
except Exception as e:
    check("MCP stdio 握手", False, repr(e)[:120])

print("== 仓库文件 ==")
for name in ("package.json", "cordis.patch.yml", "README.md", "LICENSE", "install.ps1"):
    check("存在 " + name, os.path.isfile(os.path.join(ROOT, name)))

try:
    pkg = json.load(open(os.path.join(ROOT, "package.json"), encoding="utf-8"))
    check("package.json 有 dsh.bundle.patch", bool(pkg.get("dsh", {}).get("bundle", {}).get("patch")))
    check("package.json license=MIT", pkg.get("license") == "MIT")
except Exception as e:
    check("package.json 解析", False, repr(e)[:120])

try:
    yml = open(os.path.join(ROOT, "cordis.patch.yml"), encoding="utf-8").read()
    check("cordis.patch.yml 声明 serverName", "serverName: inventor" in yml)
    check("cordis.patch.yml 用 stdio", "transport: stdio" in yml)
    # 默认配置里不应出现个人绝对路径（注释示例除外）
    bad = [ln for ln in yml.splitlines()
           if re.search(r"[A-Z]:\\\\?(?:Users|SHU Files|GU temp)", ln) and not ln.strip().startswith("#")]
    check("cordis.patch.yml 无个人绝对路径", not bad, "; ".join(bad)[:80])
except Exception as e:
    check("cordis.patch.yml 读取", False, repr(e)[:120])

try:
    src = open(os.path.join(ROOT, "run_inventor_mcp.py"), encoding="utf-8").read()
    check("run_inventor_mcp.py 无硬编码盘符路径",
          not re.search(r"['\"][A-Z]:\\\\", src))
except Exception as e:
    check("run_inventor_mcp.py 读取", False, repr(e)[:120])

print()
if fails:
    print("失败 %d 项：" % len(fails))
    for f in fails:
        print("  - " + f)
    sys.exit(1)
print("全部通过。下一步：connect()")
