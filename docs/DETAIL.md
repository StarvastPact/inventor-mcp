![Inventor MCP 桥接](preview.svg)

通过 [inventor-mcp-server](https://pypi.org/project/inventor-mcp-server/)（66 个工具）把 Autodesk Inventor 交给智能体：
`connect` → `create_document` → `create_sketch` → 画几何 → `extrude` / `revolve` → `save_document`。

## 运行方式

- 传输：stdio，由 DSH 主进程拉起子进程
- 标准方式：`python -m inventor_mcp_server.server`（依赖 `pip install inventor-mcp-server pywin32`）
- 自包含方式：`python -u <repo>/run_inventor_mcp.py`（依赖放在 `runtime/pylibs`，源码在 `runtime/ext`，不进 git）
- 语言包：mcp server 自带 40KB 的 `inventor://notes/api` 资源（枚举、单位、静默失败清单），写 `execute_python` 之前先读它

## 环境要求

- Windows + 已激活的 Autodesk Inventor（2019+，实测 2025 中文 GB 毫米模板）
- Python 3.12+（`inventor-mcp-server` 的 requires-python）
- DSH（通过 `@deepseek-ai/dsh-mcp-client` 接入）

## 已知限制

MCP server 进程必须与 Inventor 处于**同一个 Windows 会话**才能 COM 连接。
若 DSH 主进程运行在隔离会话（沙盒 shell 里直接 `Dispatch("Inventor.Application")`），
`connect` 会返回 `0x80080005`（服务器运行失败）/ `0x800401E3`（ROT 中找不到 Inventor）。
此时请在桌面会话里运行 DSH，或改用「脚本 + 桌面双击」方式。

## 慢启动

`INVENTOR_MCP_PRELOAD` 控制预热模块（默认 `numpy`）。首次 `import numpy` 可能要几十秒，
后台线程提前加载后，库导入能快一个数量级。不需要就设成空字符串。
