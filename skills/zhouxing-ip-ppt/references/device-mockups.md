# 可复用设备样机

资源目录为 `assets/device-mockups/`。先读 `manifest.json`，不凭目测猜屏幕位置。

| 模板 ID | 用途 | 默认表现 |
|---|---|---|
| iphone-14-pro-silver | 竖屏截图或视频 | 银色金属边、侧键、天线、灵动岛；周围沿用页面底色 |
| macbook-pro-screen | 横屏软件截图 | 薄边屏幕和刘海，省去键盘与底座 |

来源为 [picturepan2/devices.css](https://github.com/picturepan2/devices.css)，锁定版本见 manifest；MIT 许可原文保存在同目录 `LICENSE-Devices.css.txt`。保留 CSS 原文件、版权、源版本与衍生说明；不能把“网上免费下载”视为可再分发。当前模板为基于开源 CSS 渲染的矢量风外框，不是实拍设备，也不是 Apple 官方认证素材。模板可用性不代表用户已接受其视觉风格。

## 套入真实截图

优先直接用已经渲染好的透明外框和遮罩；普通执行不需要浏览器或重新下载。每个模板的 frame 是有透明屏幕孔的 PNG，screen_mask 是白色 alpha 遮罩，已经排除刘海/灵动岛。两者共享像素尺寸，保留三倍分辨率。模板透明边距属于资源，不是设备轮廓。

```bash
node <本Skill>/scripts/compose_device_mockup.mjs --device macbook-pro-screen --input screenshot.png --output preview.png --layers-dir device-layers
```

依赖为 Node.js 与 `@napi-rs/canvas`；从项目或 Skill 附近的 node_modules 解析，`RUNTIME_NODE_MODULES` 只作可选的已有依赖路径，详见工具适配。

脚本默认 contain，完整保留截图；不同屏幕比例产生的空余只在设备屏幕内用深色承接，不新增页内背板。`--fit cover` 会裁掉部分截图，只有确认不丢证据时使用。`--crop x,y,w,h` 按模板原始像素裁切两层，用于画布出血，不改变截图内部内容。脚本拒绝覆盖输入截图。

`device-layers/screen.png` 和 `frame.png` 是独立图层，以同一个显示框、同一缩放倍率放入 PPT；屏幕在下，外框在上。文字、数字、胶囊与箭头仍用 PPT 原生对象。保留原截图及 placement.json，换截图时重新生成屏幕层，不能把带截图的预览覆盖回通用模板。外框可移动/缩放/替换，但不是逐个侧键可编辑的原生形状。

## 校验

新增或修改模板时，用真实竖屏、横屏各试一次，检查外框中心透明、屏幕遮罩中心可见、灵动岛/刘海不透图，外框与屏幕定位一致；检查 contain 未丢关键内容。普通制作只验证本次实际使用的模板和截图，不额外测试未用模板。修改裁切后按实际画内区域重新记录 bleed_objects，目标端截图复核出血、间距及文字可读性。不能因使用模板就省略目标端验证。
