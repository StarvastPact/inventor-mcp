# Changelog

## 1.2.0

开源准备版。

- `cordis.patch.yml` 默认改为 `python -m inventor_mcp_server.server`（pip 安装即可用），不再写死本机绝对路径
- 新增 `install.ps1`：自动检测 Python 3.12+、安装 `inventor-mcp-server` / `pywin32`、把配置里的解释器改成绝对路径
- 新增 `README.md`、`LICENSE`（MIT）、`.gitignore`、`docs/TOOLS.md`
- `docs/DETAIL.md` 去掉个人路径，改为通用环境要求说明
- `runtime/`（pylibs + 第三方源码 + 日志）不再进版本控制，作为可选离线模式

## 1.1.0

- `run_inventor_mcp.py` 改为从自身位置推导所有路径，无硬编码
- 启动日志同时写 `runtime/logs/server.log` 与 stderr，日志目录不可写时静默降级
- `cordis.patch.yml` 用 PATH 里的 `python` 替代写死解释器路径

## 1.0.0

- 首个可用版本：DSH bundle + stdio 桥接 inventor-mcp-server 1.2.1
- 验证：参数化 V 带轮（16 个用户参数、3 个全约束草图、体积/包围盒端到端可复现）
