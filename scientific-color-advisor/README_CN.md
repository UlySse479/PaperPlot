# Scientific Color Advisor

[English README](./README.md)

Scientific Color Advisor 是一个面向 Agent Skills 场景的科学配色仓库，聚焦科研图表配色和 PPT 色彩系统。仓库内置本地 Node CLI、一个 vendored 的 [Scientific-Color-Lab](https://github.com/groele/Scientific-Color-Lab) 快照、诊断评分逻辑，以及适合绘图工作流的导出结果。

## 功能概览

- 为折线图、散点图、柱状图、热图、概念图和演示文稿推荐配色
- 支持两个目标：`scientific-figure` 和 `ppt`
- 返回排序后的推荐结果、HEX 列表、诊断信息、快速修复建议和可复用导出载荷
- 支持导出 `matplotlib`、`plotly`、`matlab`、`css`、`json`、`summary`
- 为 PPT 生成标题、正文、强调色和图表色的 role pack
- 默认以 vendored 模式运行，也可以按需检查本地 `Scientific-Color-Lab` 仓库

## 安装

通过 GitHub 安装 skill：

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo OWNER/scientific-color-advisor --path skill
```

把 `OWNER` 替换为仓库所在 GitHub 账号，然后重启客户端。

适合支持 skill 安装的 coding agent 的自然语言提示：

```text
Install the scientific-color-advisor skill from GitHub repo OWNER/scientific-color-advisor path skill.
```

如果目标 agent 不直接支持 Agent Skills 格式，也可以先 clone 仓库，再按下面的 CLI 示例使用。

## 快速开始

推荐一个适合论文折线图的安全配色：

```bash
node skill/scripts/scientific-color-cli.mjs recommend --target scientific-figure --chart-type line-plot --palette-class qualitative --usage manuscript --background light --tone restrained --priority colorblind-safe --priority avoid-red-green
```

生成一个 PPT 色彩系统的 JSON 输出：

```bash
node skill/scripts/scientific-color-cli.mjs recommend --target ppt --chart-type presentation-slide --palette-class qualitative --usage course-slides --background dark --tone strong --output json
```

导出热图推荐：

```bash
node skill/scripts/scientific-color-cli.mjs export --target scientific-figure --chart-type heatmap --palette-class sequential --usage poster --background dark --tone strong --format matplotlib --format css
```

检查运行模式和本地仓库兼容性：

```bash
node skill/scripts/scientific-color-cli.mjs doctor --repo /path/to/Scientific-Color-Lab
```

## 效果示例

下面这些示例都来自仓库当前 CLI 的真实输出，目的是让读者快速判断它到底能产出什么。

### 1. 论文风格折线图推荐

命令：

```bash
node skill/scripts/scientific-color-cli.mjs recommend --target scientific-figure --chart-type line-plot --palette-class qualitative --usage manuscript --background light --tone restrained --priority colorblind-safe --priority avoid-red-green
```

结果摘要：

- 模板：`Manuscript Cool`
- 适用原因：偏克制、适合论文、规避明显红绿冲突
- 快速修复建议：`increase-categorical-spacing`、`suggest-safer-template`

固定快照：

![论文折线图快照](./docs/generated/line-plot-example.svg)

### 2. 深色热图导出

命令：

```bash
node skill/scripts/scientific-color-cli.mjs export --target scientific-figure --chart-type heatmap --palette-class sequential --usage poster --background dark --tone strong --format matplotlib --format css
```

选中模板：

- `Magma Dark Heatmap Dark`

导出片段：

```python
scientific_color_lab = [
    {"name": "magma-dark-heatmap-dark 1", "hex": "#000004"},
    {"name": "magma-dark-heatmap-dark 5", "hex": "#9E2F7F"},
    {"name": "magma-dark-heatmap-dark 9", "hex": "#FCFDBF"},
]
```

```css
:root {
  --magma_dark_heatmap_dark-1: #000004;
  --magma_dark_heatmap_dark-5: #9E2F7F;
  --magma_dark_heatmap_dark-9: #FCFDBF;
}
```

固定快照：

![深色热图导出快照](./docs/generated/heatmap-export-example.svg)

### 3. PPT 角色配色包

命令：

```bash
node skill/scripts/scientific-color-cli.mjs recommend --target ppt --chart-type presentation-slide --palette-class qualitative --usage course-slides --background dark --tone strong
```

结果摘要：

- 模板：`Slide Minimal Dark`
- 标题色：`#F6F5F1`
- 正文色：`#E8E4DE`
- 强调色：`#274F69`、`#AF845F`、`#D9D2CA`

固定快照：

![PPT 角色配色包快照](./docs/generated/ppt-role-pack-example.svg)

## 仓库结构

```text
scientific-color-advisor/
|-- skill/
|   |-- SKILL.md
|   |-- agents/openai.yaml
|   |-- references/
|   |-- scripts/scientific-color-cli.mjs
|   `-- vendor/scientific-color-lab-core/
|-- tests/
|-- tools/
|-- package.json
`-- THIRD_PARTY_NOTICES.md
```

## CLI 命令

### `recommend`

返回排序后的推荐配色、诊断信息和使用建议。

常用参数：

- `--target scientific-figure|ppt`
- `--chart-type line-plot|scatter-plot|bar-chart|heatmap|concept-figure|presentation-slide`
- `--palette-class qualitative|sequential|diverging|cyclic|concept`
- `--usage manuscript|lab-meeting|poster|course-slides|online-document`
- `--background light|dark`
- `--tone restrained|balanced|strong`
- `--priority <flag>` 可重复
- `--source-color <hex>` 可重复
- `--output human|json`

### `export`

为当前最佳推荐构建导出结果。

额外参数：

- `--format matplotlib|plotly|matlab|css|json|summary|ppt-pack`

### `doctor`

输出 vendored 元数据、运行模式和可选的本地仓库检查结果。

## 本地仓库桥接

默认使用 vendored 模式。只有在用户明确要求对接本地 [`Scientific-Color-Lab`](https://github.com/groele/Scientific-Color-Lab) 仓库时，才使用本地桥接。

可以通过以下任一方式指定：

- `--repo /path/to/Scientific-Color-Lab`
- `SCIENTIFIC_COLOR_LAB_REPO=/path/to/Scientific-Color-Lab`

当前本地桥接会检查：

- 上游目录结构是否符合预期
- 实时模板目录是否可用
- 如果 Git 元数据存在，则检查上游 commit 身份

## 开发

重新生成 README 示例快照：

```bash
node tools/generate-readme-examples.mjs
```

同步 vendored 模板数据：

```bash
node tools/sync-vendor-from-upstream.mjs /path/to/Scientific-Color-Lab
```

运行测试：

```bash
npm test
```

运行仓库校验：

```bash
node tools/validate-release.mjs
```

只运行 skill frontmatter 校验：

```bash
node tools/validate-skill.mjs
```

## 兼容性

- Node.js 20+
- vendored 模板快照固定在 `skill/vendor/scientific-color-lab-core/metadata.json`
- 协议版本：`1`

## 归属与致谢

本仓库 vendored 了一份来自 [Scientific-Color-Lab](https://github.com/groele/Scientific-Color-Lab) 的最小模板快照及派生元数据。详见 [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md)。
