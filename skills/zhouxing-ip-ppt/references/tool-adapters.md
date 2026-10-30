# 工具能力与 agent 适配

核心流程是读取内容、规划图文关系、准备角色/截图、写入原生对象、测量并在目标端复核。按能力选工具，不把某个平台的函数名或安装路径作为技能前提。

| 所需能力 | 通用要求 | Codex 可选路径 |
|---|---|---|
| 读图与文件 | 能读本 Skill 相对资源和用户素材 | 文件工具与 view_image |
| 生成角色/场景 | 支持参考图实际输入；透明背景或可保留 alpha | imagegen Skill / image_gen，参数按当前工具说明 |
| 原生 PPTX | 可创建独立文字、形状、图片；可导出 PPTX | presentations Skill / @oai/artifact-tool |
| 飞书原生稿 | 已授权的幻灯片连接器或 lark-cli | lark-slides / lark-shared；CLI 本身不限 Codex |
| 字形、透明轮廓与样机套图 | Node.js、@napi-rs/canvas；字体在目标机可用 | 可选使用已提供的 bundled Node/依赖 |
| 计划与间距检查 | Python 3 标准库 | 相同脚本，无 Codex API |
| 目标端预览 | PPTX 阅读/渲染器、幻灯片截图 API 或应用预览 | 本地渲染和飞书截图 |

## 其他 agent 的使用方式

复制整个 `zhouxing-ip-ppt` 目录到目标 agent 的技能目录，保留 SKILL.md、references、scripts、assets。若目标不支持技能目录，让它以 SKILL.md 为入口，并能按需读取相对资源。只复制主文档会丢失风格母图、样机和协议。

`agents/openai.yaml` 仅供 Codex UI 显示名称和默认提示；其他 agent 可忽略或省略，不承担执行逻辑。无需同步其他 Codex 配置、账号、执行对话或本机私有路径。本 Skill 不内置用户文章、账号截图或演示稿。

目标环境需要三类能力：生图（或已提供匹配图片）、可编辑幻灯片写入、预览。缺少某一项时说明具体限制；不能因为没有同名 Skill 就认定没有等效工具，也不能把工具缺失写成已经完成。首次使用先用一页角色、一页截图和一页较多正文做端到端小测试；用户已明确要求整套时，把能力测试纳入执行，不额外卡在审批步骤。

## 脚本依赖

`validate_plan.py` 和 `audit_layout.py` 只使用 Python 标准库。两个 `.mjs` 入口通过 `canvas_runtime.mjs` 解析 @napi-rs/canvas：先尝试 Skill 附近和当前工作项目的 node_modules，再尝试可选环境变量 RUNTIME_NODE_MODULES 指定的已有目录。

普通项目已具备依赖时，直接运行：

```bash
node <skill-root>/scripts/measure_layout.mjs objects.json measured.json
python3 <skill-root>/scripts/audit_layout.py measured.json
node <skill-root>/scripts/compose_device_mockup.mjs --device iphone-14-pro-silver --input screenshot.png --output preview.png --layers-dir device-layers
```

缺依赖时，可按目标环境的包管理和权限规则在工作项目安装 `@napi-rs/canvas`；也可使用等效的文字渲染、PNG alpha 测量与合成工具，保留相同几何与验证目的。不要复制另一个平台的整套运行时。当前目录影响依赖查找；素材路径则以输入 JSON 的 asset_base 解析，font_files 中的相对字体路径也相对该目录。字体不随本 Skill 分发，使用目标机实际可用的字体，并记录同类替代。

## 测试边界

脚本和资源能在本地解包后运行，不等于某个其他 agent 已完成端到端制作。模型的构图判断、生图工具的参考遵循度、PPTX 引擎和目标字体仍会改变效果。迁移后复核真实输出，不把“通用接口”称为“所有平台效果一致”。
