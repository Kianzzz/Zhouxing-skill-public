# 开源调研

日期 2026-10-29（用户时区）。读了一手仓库/官方文档及下列源文件，没有安装或端到端运行全部引擎，不把 README 宣传当效果证明。

| 项目 | 具体来源 | 学习点与选择 |
|---|---|---|
| [PptxGenJS](https://github.com/gitbrent/PptxGenJS) | [Text API](https://gitbrent.github.io/PptxGenJS/docs/api-text/) | 显式坐标、fontSize/fontFace、margin、段间距、混排 runs；用于理解原生 PPTX 的格式控制；可按环境选择原生 PPTX 写入引擎，工具适配见主文档链接。API 样例不是美学标准 |
| [python-pptx](https://github.com/scanny/python-pptx) | [Working with text](https://python-pptx.readthedocs.io/en/latest/user/text.html)、[适配分析](https://python-pptx.readthedocs.io/en/latest/dev/analysis/txt-autofit-text.html) | shape/text frame/paragraph/run 分层；缩字与扩框机制不同，适配依赖字体；用于理解文本模型，不作为当前执行入口；不把 fit_text 当设计策略 |
| [Slidev](https://github.com/slidevjs/slidev) | [two-cols.vue](https://github.com/slidevjs/slidev/blob/main/packages/client/layouts/two-cols.vue)、[主题 layouts.css](https://github.com/slidevjs/themes/blob/main/packages/theme-default/styles/layouts.css)、[导出](https://sli.dev/guide/exporting) | 实际源码双列 grid/左右 slot；普通标题、cover、fact、statement 不同层级。文档有普通图片式与 pptx-editable 两种；后者本机未测，优先飞书原生 |
| [Marp CLI](https://github.com/marp-team/marp-cli) | [README](https://github.com/marp-team/marp-cli#experimental-generate-editable-pptx---pptx-editable) | 普通 PPTX 预渲染为图；editable 是实验特性，需浏览器和 LibreOffice，官方提示复杂样式与保真风险。不作为默认交付引擎 |
| [Presenton](https://github.com/presenton/presenton) | [editorial/template.json](https://github.com/presenton/presenton/blob/main/templates/editorial/template.json) | 已读模板的 fonts 映射、merged_components、position/size、decorative、layers/variants，学习结构化模板和内容/装饰分离，不复制深色风格或引入整套服务 |
| [Lark CLI](https://github.com/larksuite/cli) | [原生创建](https://github.com/larksuite/cli/blob/main/skills/lark-slides/references/cli/lark-slides-create.md)、本机 help/schema | XML 原生对象、按页写入、媒体上传；版本参数有漂移，运行时检查本机接口 |

事实：这些实现区分主题、布局、文本、素材与导出。推断：本工作流也应先确定页面语义和几何，再生成适配动作，最后原生排版。

事实：Slidev 主题针对普通页、封面、fact 等分别设置字体层级。设计建议：封面/内容/数据页使用不同标题与角色尺度，仍共享字体和间距系统。具体数值来自参考分析和本 Skill 选择，不是项目统一规范。

事实：部分网页工具普通 PPTX 为图片。结论：扩展名不能证明可编辑，需看原生对象与目标端行为。

能力边界：开源引擎在本机可用性、PPTX 导入飞书保真、真人多动作一致性与目标端编辑效果都需按任务实测；CLI 身份有效不等于创建成功，回读成功也不等于手动编辑已测。
