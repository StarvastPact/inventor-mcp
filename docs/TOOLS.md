# 工具清单

按用途分组。参数细节在 MCP 工具签名里（每个工具都带完整 docstring）。

## 连接与状态

| 工具 | 作用 |
|---|---|
| `connect` | 连上运行中的 Inventor；可按 `.ipj` 项目连、可强制新实例、可按 pid 连 |
| `list_instances` | 已连的 Inventor 列表 + 连不上的手工实例 |
| `get_status` | 连接状态、活动文档、execute_python 命名空间年龄 |
| `manage_documents` | 列出/打开/激活/关闭文档，`close_all` 可顺带退出 Inventor |
| `manage_call` | 跟进或取消一次超时的调用（长时间 `execute_python`、卡在对话框） |
| `reload_api` | 改完包源码后热重载，不必重启 server |

## 文档与参数

| 工具 | 作用 |
|---|---|
| `create_document` | 建零件/钣金/装配，可同时设材料、件号、描述 |
| `save_document` | 安全保存（不开对话框、不覆盖库文件、依赖逐个先存） |
| `inspect_model` | 一次拿到体积、包围盒、面/边数、特征树、草图、警告 |
| `edit_properties` | 读写 iProperties（件号、描述、材料、质量、自定义字段） |
| `manage_parameters` | 读/改/加用户参数（`rim_od = 110 mm`） |

## 草图

| 工具 | 作用 |
|---|---|
| `create_sketch` | 工作平面（XY/XZ/YZ）、体表面，或偏移平面 |
| `draw_line` / `draw_circle` / `draw_arc` | 线、圆（自动加直径尺寸）、弧 |
| `draw_rectangle` | 中心矩形，可带圆角（半宽 = 腰形孔） |
| `draw_slot` / `draw_polygon` | 腰形孔、正多边形 |
| `draw_closed_profile` | 一次画出闭合轮廓，支持圆角与三点圆弧 |
| `draw_pattern` | 草图内阵列（圆孔/腰形/矩形），圆形或网格 |
| `offset_profile` | 每个闭合环偏移（密封槽、壁厚、留边） |
| `project_edges` | 把实体边投影进草图（引用几何） |
| `check_sketch` | 诊断：开口、缝隙、三重交汇、重复线，以及能否成轮廓 |

## 实体特征

| 工具 | 作用 |
|---|---|
| `extrude` | 拉伸/切除/求交/曲面/新实体，可 `extent_type=all` 贯穿 |
| `revolve` | 绕轴旋转（含切割，如轮槽） |
| `sweep` / `loft` | 扫掠、放样 |
| `shell` | 抽壳 |
| `fillet` / `chamfer` | 圆角、倒角（切向边自动跟随） |
| `add_hole` | 原生孔特征：直孔、ISO 米制螺纹、沉头 |
| `add_mirror` | 特征镜像或整体镜像（可只留镜像侧） |
| `add_circular_pattern` / `add_rectangular_pattern` | 特征阵列 |
| `manage_features` | 列出/删除/抑制特征 |

## 钣金

| 工具 | 作用 |
|---|---|
| `manage_sheet_metal_rules` | 规则（厚度+折弯半径一起改） |
| `add_sheet_metal_face` | 首块平板 |
| `add_flange` | 折弯边，一圈边一次调用自动斜接 |
| `sheet_metal_cut` | 按板厚贯穿的切口 |
| `add_corner_round` | 折弯件角部圆角（展开图跟随） |
| `add_sheet_profile` | 整根折弯型材（L/U/C/Z/帽形） |
| `export_flat_pattern` | 展开图 + DXF（外层/内孔/折弯线分层） |
| `check_manufacturability` | 可制造性：V 模、最小翻边、孔到折弯距离、板材尺寸 |

## 装配

| 工具 | 作用 |
|---|---|
| `place_components` | 批量放置零件/子装配，可指定位置与轴向、接地 |
| `manage_occurrences` | 列表/查找/接地/删除/替换/坐标换算 |
| `constrain` / `manage_constraints` | 配合/齐平/角度/插入约束，改偏移、删约束 |
| `measure_distance` | 两个 occurrence 的最小距离 |
| `check_interference` | 干涉检查（体积 + 包围盒） |
| `check_fastener_alignment` | 贴合面上的孔是否对齐、被挡、能过多大螺栓 |
| `sweep_rotation` | 按角度扫掠转动件，报告每个角度的碰撞 |
| `add_assembly_cut` | 装配级打孔（不动零件文件） |
| `add_frame_members` | 按骨架线布型材（Frame Generator 的 API 替代）+ 下料表 |

## Content Center、导入与出图

| 工具 | 作用 |
|---|---|
| `use_content_center` | 浏览标准件库、按规格生成零件 |
| `import_step` | 导入厂商 STEP 为 Inventor 文件，返回包围盒/体积 |
| `convert_surfaces_to_solid` | 曲面缝合补洞转实体（处理无体量的导入模型） |
| `create_drawing` | 出工程图 PDF：基本视图、投影视图、尺寸、剖视、局部放大、BOM、气泡 |
| `export_document` | STEP / IGES / SAT / STL |
| `export_bom` | BOM（零件汇总或结构化），可导 CSV |
| `capture_view` | 截渲染图（等轴测/六个标准视图/自定义相机），可隔离、可显示草图 |

## 底层与工具

| 工具 | 作用 |
|---|---|
| `execute_python` | 对活连接执行任意 Python（持久命名空间，预绑定 inv/app/doc/comp/body/tg） |
| `load_library` | 把常用 helper 文件载入命名空间并记住 |
| `transaction` | begin/commit/abort，多步操作一个撤销单元 |
| `find_faces` / `find_edges` | 按类型/方向/位置/尺寸找面或边 |
| `manage_materials` | 批量查/设材料，找「还是 Generic」的零件 |

## 单位与坑

- **MCP 层全部是 mm**；底层 COM 是 cm，转换在包内完成。
- `execute_python` 里直接碰 COM 时记得 /10。
- 写代码前读资源 `inventor://notes/api`：枚举值、静默失败的调用、返回 tuple 的接口都在那里。
