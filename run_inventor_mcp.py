# -*- coding: utf-8 -*-
"""inventor-mcp server 启动器（stdio 传输）。

自动选择两种运行模式，一份配置通吃：
  A. pip 模式：系统 Python 已 `pip install inventor-mcp-server` → 直接 import 调用
  B. 自包含模式：使用仓库内 runtime/pylibs + runtime/ext 的副本（离线、免 pip）

自包含目录结构：
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
EXT_ROOT = os.path.join(RUNTIME, "ext")


class Tee:
    """把 stderr 同时写到文件和调用方 stderr。日志打不开时只走 stderr，不崩溃。"""

    def __init__(self, path):
        self._f = None
        self._err = sys.__stderr__
        try:
            self._f = open(path, "a", encoding="utf-8", buffering=1)
        except Exception:
            self._f = None

    def write(self, s):
        try:
            if self._f:
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


def _add_pylibs():
    """把仓库内的依赖目录挂上 sys.path；不存在则返回 False（交给系统环境）。"""
    if not os.path.isdir(PYLIBS):
        return False
    sys.path.insert(0, PYLIBS)
    for sub in ("win32", os.path.join("win32", "lib"), "win32comext"):
        p = os.path.join(PYLIBS, sub)
        if os.path.isdir(p) and p not in sys.path:
            sys.path.append(p)
    dll = os.path.join(PYLIBS, "pywin32_system32")
    if os.path.isdir(dll):
        os.add_dll_directory(dll)
    return True


def _find_server_script():
    """在 runtime/ext 下找 inventor_mcp_server/server.py，版本目录名不写死。"""
    if not os.path.isdir(EXT_ROOT):
        return None
    for name in sorted(os.listdir(EXT_ROOT), reverse=True):
        p = os.path.join(EXT_ROOT, name, "inventor_mcp_server", "server.py")
        if os.path.isfile(p):
            return p
    return None


def _check_pywin32(log):
    try:
        import pythoncom  # noqa: F401
        import win32com.client  # noqa: F401

        log("[boot] pywin32 OK (%s)" % getattr(pythoncom, "__file__", "?"))
        return True
    except Exception:
        log("[FATAL] pywin32 导入失败:\n" + traceback.format_exc())
        return False


def main():
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except Exception:
        pass
    sys.stderr = Tee(os.path.join(LOG_DIR, "server.log"))
    log = lambda msg: print(msg, file=sys.stderr)  # noqa: E731

    log("[%s] boot python=%s here=%s"
        % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
           sys.version.split()[0], HERE))

    if _add_pylibs():
        log("[boot] pylibs on path: %s" % PYLIBS)
    else:
        log("[boot] no runtime/pylibs, falling back to system site-packages")

    if not _check_pywin32(log):
        return 3

    # A. pip 模式：系统里装过 inventor-mcp-server
    try:
        from inventor_mcp_server import server as srv

        log("[boot] mode=pip %s" % getattr(srv, "__file__", "?"))
        srv.main()
        return 0
    except ImportError:
        pass

    # B. 自包含模式：仓库自带的副本
    script = _find_server_script()
    if not script:
        log("[FATAL] 找不到 inventor_mcp_server：既未 pip 安装，runtime/ext 下也没有副本")
        return 2
    log("[boot] mode=bundled %s" % script)
    runpy.run_path(script, run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())
