# -*- coding: utf-8 -*-
"""inventor-mcp server 启动器（stdio 传输）。

目录结构自动推导，不含任何写死的绝对路径：

    inventor-mcp/
      run_inventor_mcp.py              <- 本文件
      runtime/pylibs/                  <- Python 依赖（mcp、pywin32 等）
      runtime/ext/<server>/            <- inventor_mcp_server 源码
      runtime/logs/server.log          <- 启动与崩溃日志

日志只写 stderr 与文件，绝不写 stdout —— stdio 传输的 stdout 是协议通道。
"""
import datetime
import os
import runpy
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
RUNTIME = os.path.join(HERE, "runtime")
PYLIBS = os.path.join(RUNTIME, "pylibs")
LOG_DIR = os.path.join(RUNTIME, "logs")
SERVER = os.path.join(
    RUNTIME, "ext", "inventor_mcp_server-1.2.1", "inventor_mcp_server", "server.py"
)
LOG = os.path.join(LOG_DIR, "server.log")


class Tee:
    """把 stderr 同时写到文件和调用方的 stderr。日志打不开时只走 stderr，不崩溃。"""

    def __init__(self, path):
        self._f = None
        self._err = sys.__stderr__
        try:
            self._f = open(path, "a", encoding="utf-8", buffering=1)
        except Exception:
            self._f = None

    def write(self, s):
        try:
            self._f.write(s)
        except Exception:
            pass
        try:
            if self._err:
                self._err.write(s)
        except Exception:
            pass
        return len(s)

    def flush(self):
        for o in (self._f, self._err):
            try:
                if o:
                    o.flush()
            except Exception:
                pass

    def isatty(self):
        return False


def preflight():
    """启动前自检，返回问题列表（空列表表示可以启动）。"""
    problems = []
    if not os.path.isdir(PYLIBS):
        problems.append("缺少依赖目录 runtime/pylibs")
    if not os.path.isfile(SERVER):
        problems.append(
            "缺少 MCP 服务器 runtime/ext/inventor_mcp_server-1.2.1/"
            "inventor_mcp_server/server.py"
        )
    return problems


def main():
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except Exception:
        pass
    sys.stderr = Tee(LOG)
    log = lambda msg: print(msg, file=sys.stderr)  # noqa: E731

    log(
        "[%s] boot python=%s here=%s"
        % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
           sys.version.split()[0], HERE)
    )

    problems = preflight()
    if problems:
        for p in problems:
            log("[FATAL] " + p)
        return 2

    sys.path.insert(0, PYLIBS)
    for sub in ("win32", os.path.join("win32", "lib"), "win32comext"):
        p = os.path.join(PYLIBS, sub)
        if os.path.isdir(p) and p not in sys.path:
            sys.path.append(p)
    dll = os.path.join(PYLIBS, "pywin32_system32")
    if os.path.isdir(dll):
        os.add_dll_directory(dll)

    try:
        import pythoncom  # noqa: F401
        import win32com.client  # noqa: F401

        log("[boot] pywin32 import OK (pythoncom=%s)"
            % getattr(pythoncom, "__file__", "?"))
    except Exception:
        log("[FATAL] pywin32 导入失败:\n" + traceback.format_exc())
        return 3

    log("[boot] starting " + SERVER)
    runpy.run_path(SERVER, run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())
