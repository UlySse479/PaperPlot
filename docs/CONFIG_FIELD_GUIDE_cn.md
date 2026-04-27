# PaperPlot 配置字段与调图速查手册

这份文档专门解决两个高频问题：

1. 某个配置应该写在 `figure` 下，还是写在 `override` 下？
2. 我想改某种显示效果时，应该改哪个组件、哪个字段？

如果你已经会写基础 config，但在“参数该放哪”和“该查哪个层级”上反复犹豫，这份文档就是给你准备的。

## 一句话规则

先记住最重要的一句：

* 改“这张图要画什么、怎么画”时，优先写在 `figure`
* 改“整张图的视觉 token / Matplotlib 风格细节”时，写在 `override`

更具体一点：

* `paper`：选论文 profile 和 style
* `figure`：选模板、传数据、指定坐标映射、打开某个功能、设置某张图的显示行为
* `override`：对最终样式 spec 做补丁，改字体、线宽、网格、figure 尺寸、palette 等底层 token

---

## 配置结构总览

一个典型配置长这样：

```yaml
paper:
  profile: icml
  style: academic-muted

figure:
  template: line.sota_compare
  data:
    epoch: [1, 2, 3, 1, 2, 3]
    acc: [70, 73, 75, 68, 71, 74]
    method: [A, A, A, B, B, B]
  x: epoch
  y: acc
  hue: method
  title: Training Curve
  legend: upper left
  legend_bbox_to_anchor: [0.0, 1.02]
  override:
    axes.grid: true
    lines.linewidth: 2.3
    font.size: 8
```

这里三层分别负责：

* `paper.profile`：论文尺寸、字号、字体家族、导出规格
* `paper.style`：默认配色、网格、线宽、legend 基础风格
* `paper.color_advisor`：自动推荐科研配色，并为整篇论文维护稳定的标签到颜色映射
* `figure.*`：这张图的内容和显示行为
* `figure.override`：对最终 spec 的底层覆盖

---

## `paper.color_advisor` 什么时候该用

如果你的目标不是“手工填一组 HEX”，而是：

* 让不同图种自动挑更稳妥的科研配色
* 避免红绿冲突、灰度下失真、论文缩小后辨识度下降
* 让 `Ours`、`Baseline`、`Teacher` 这类标签在整篇论文里始终对应同一种颜色

那这个配置应该写在 `paper.color_advisor`，而不是 `figure.override.palette.colors`。

最常见写法：

```yaml
paper:
  profile: icml
  style: academic-muted
  color_advisor:
    enabled: true
    usage: manuscript
    tone: restrained
    priorities: [colorblind-safe, grayscale-safe, avoid-red-green]
    namespace: my-paper
    persist_path: .paperplot/paper-colors.json
    preferred_order: [Ours, Baseline, Ablation]
    bindings:
      Ours: primary
      Baseline: secondary
```

这些字段分别解决不同问题：

* `enabled`：是否启用自动推荐
* `usage`：面向论文、海报还是在线文档
* `tone`：更克制还是更强调
* `priorities`：是否优先规避红绿冲突、提升灰度可读性等
* `namespace`：为同一项目的多张图共享一套颜色映射
* `persist_path`：把映射落盘，分别渲染多张图时仍保持稳定
* `preferred_order`：让关键系列优先占用主色
* `bindings`：显式把某个标签固定到 `primary` / `secondary` / `color-3`

一句话区分：

* `paper.color_advisor`：解决“整篇论文怎么统一配色”
* `figure.override.palette.colors`：解决“这一张图我想临时手改几种颜色”

---

## 什么时候写在 `figure`，什么时候写在 `override`

### 第一判断：它是不是“当前图的语义参数”

如果这个参数描述的是“这张图画什么、怎么画、显示哪些元素”，放在 `figure`。

常见例子：

* `template`
* `data`
* `x` / `y` / `hue`
* `title`
* `xlabel` / `ylabel`
* `legend`
* `legend_title`
* `legend_bbox_to_anchor`
* `legend_ncol`
* `extra_legends`
* `xlim` / `ylim`
* `xticks` / `yticks`
* `marker`
* `markers`
* `linestyles`
* `reference_lines`
* `text_annotations`
* `annotate`
* `annotate_points`
* `pareto_frontier`
* `significance`
* `show_value_labels`
* `value_label_format`
* `orientation`
* `global_legend`
* `panels`
* `elements`

这类参数通常满足一个特点：你换一张图，这些值很可能也会跟着变。

### 第二判断：它是不是“风格 token / Matplotlib rcParams 级别参数”

如果这个参数是在调视觉系统，而不是在定义这张图的语义，放在 `override`。

常见例子：

* `axes.grid`
* `axes.grid_alpha`
* `axes.grid_linewidth`
* `axes.edgecolor`
* `axes.linewidth`
* `axes.tick_size`
* `axes.tick_width`
* `font.family`
* `font.size`
* `font.title_size`
* `font.label_size`
* `font.tick_size`
* `lines.linewidth`
* `lines.markersize`
* `lines.markeredgewidth`
* `legend.fontsize`
* `legend.title_fontsize`
* `legend.handlelength`
* `palette.colors`
* `figure.figsize`
* `template.defaults.*`

这类参数通常满足另一个特点：你换了数据，甚至换了模板，它们也未必需要跟着变。

---

## 最实用的判断表

| 你想改什么 | 放哪里 | 原因 |
| --- | --- | --- |
| 模板类型 | `figure.template` | 这是图种选择，不是样式补丁 |
| 数据源 | `figure.data` | 这是图内容 |
| 横轴 / 纵轴 / hue 映射 | `figure.x` / `figure.y` / `figure.hue` | 这是图语义 |
| 标题和坐标轴标题 | `figure.title` / `figure.xlabel` / `figure.ylabel` | 这是图内文本内容 |
| legend 位置 | `figure.legend` / `figure.legend_bbox_to_anchor` | 这是这张图的布局行为 |
| 增加一个额外 legend | `figure.extra_legends` | 这是显示行为 |
| 坐标范围和刻度 | `figure.xlim` / `figure.ylim` / `figure.xticks` / `figure.yticks` | 这是当前图的读数设置 |
| 开启显著性标注 | `figure.significance` | 这是当前图的解释元素 |
| 加参考线 / 文本标注 | `figure.reference_lines` / `figure.text_annotations` | 这是当前图的说明元素 |
| 是否显示 marker | `figure.marker` | 这是当前图的折线表达方式 |
| 每条线的 marker 或 linestyle | `figure.markers` / `figure.linestyles` | 这是当前图的线条编码方式 |
| 改全局颜色板 | `figure.override.palette.colors` | 这是 style token |
| 改线宽、字号、网格透明度 | `figure.override.*` | 这是视觉 token |
| 改图像物理尺寸 | `figure.size` 或 `figure.override.figure.figsize` | 命名尺寸用 `size`，精确尺寸用 `override.figure.figsize` |

---

## 最容易混淆的几组参数

### 1. `title` 和 `template.defaults.title`

优先级上都能影响标题，但用途不同。

什么时候用 `figure.title`：

* 你只是在改这一张图的标题
* 这是 config 里最直接、最清晰的写法

什么时候用 `override.template.defaults.title`：

* 你想临时改模板默认值，而不是只改一个最终渲染字段
* 这种写法通常只在你明确知道模板默认结构时才值得用

实际建议：

* 单图改标题，优先用 `figure.title`
* 除非你确实在调模板默认行为，否则不要优先碰 `template.defaults.*`

### 2. `legend` 和 `override.legend.loc`

两者都和 legend 位置有关，但建议优先使用 `figure.legend`。

为什么：

* `figure.legend` 是 plotter 明确支持的运行时参数
* `override.legend.loc` 更偏底层 spec，读配置的人不容易第一眼看懂

实际建议：

* 改 legend 位置，优先用 `figure.legend`
* 改 legend 字号、handle length，才用 `override.legend.*`

### 3. `size` 和 `override.figure.figsize`

什么时候用 `figure.size`：

* 你想用 profile 里定义好的命名尺寸
* 常见值：`single` / `double` / `square`

什么时候用 `override.figure.figsize`：

* 你想指定精确英寸尺寸，例如 `[6.4, 3.2]`
* 你在做论文排版微调，需要精确卡宽高

实际建议：

* 常规使用先试 `size`
* 只有在排版已经进入精修阶段时再上 `figure.figsize`

### 4. `paper.style` 和 `figure.override.palette.colors`

什么时候换 `paper.style`：

* 你想整体换一套视觉语言
* 例如从 `academic-muted` 换到 `grayscale-safe`

什么时候用 `override.palette.colors`：

* 你只想在当前图上临时换一组颜色
* 你不想新建 style 资源

实际建议：

* 如果风格切换会复用，多半该换 `style`
* 如果只是单图小修，才用 `override.palette.colors`

---

## 反查手册：想改什么，该用什么

下面这一节按“目标效果”来查，不按底层模块组织。

### A. 想改图的数据和图种

| 目标 | 用什么 |
| --- | --- |
| 换成折线图 / 柱状图 / 热力图 | `figure.template` |
| 换数据 | `figure.data` |
| 改 x / y / hue 对应的列 | `figure.x` / `figure.y` / `figure.hue` |
| 复合图里改某个 panel | `figure.panels[i].*` 或 `figure.elements[i].*` |

例子：

```yaml
figure:
  template: scatter.pareto_frontier
  data: my_points.csv
  x: latency
  y: score
  labels: method
```

### B. 想改标题、坐标轴和刻度

| 目标 | 用什么 |
| --- | --- |
| 改图标题 | `figure.title` |
| 改 x / y 轴标题 | `figure.xlabel` / `figure.ylabel` |
| 限制坐标轴范围 | `figure.xlim` / `figure.ylim` |
| 指定坐标轴刻度 | `figure.xticks` / `figure.yticks` |
| 改刻度格式 | `figure.xformatter` / `figure.yformatter` |
| 改对数坐标 | `figure.xscale` / `figure.yscale` |

例子：

```yaml
figure:
  xlim: [0, 200]
  ylim: [0.62, 0.79]
  xticks: [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200]
```

### C. 想改 legend

这是最常见的困惑点之一。

#### 主 legend 的位置和形式

| 目标 | 用什么 |
| --- | --- |
| 改 legend 位置 | `figure.legend` |
| 精确偏移 legend | `figure.legend_bbox_to_anchor` |
| 改 legend 标题 | `figure.legend_title` |
| legend 横向排几列 | `figure.legend_ncol` |

例子：

```yaml
figure:
  legend: upper left
  legend_title: Model
  legend_bbox_to_anchor: [0.0, 1.02]
  legend_ncol: 2
```

#### 增加额外 legend

适用场景：

* 一组 legend 表示模型
* 另一组 legend 表示线型含义 / baseline / metric

用什么：

* `figure.extra_legends`

例子：

```yaml
figure:
  extra_legends:
    - title: Metric
      loc: lower right
      entries:
        - label: Main Curve
          color: "#666666"
          linestyle: "--"
        - label: Baseline
          color: "#999999"
          linestyle: "-"
```

#### 复合布局里的全局 legend

适用组件：

* `subplots.default`
* `table_mix.default`
* `table_mix.paper_summary`

用什么：

* `figure.global_legend: true`
* 再配合 `figure.legend` / `figure.legend_bbox_to_anchor` / `figure.legend_ncol`

例子：

```yaml
figure:
  template: subplots.default
  global_legend: true
  legend: upper center
  legend_bbox_to_anchor: [0.5, 1.03]
  legend_ncol: 3
```

#### legend 的字体和视觉风格

这时不要去 `figure.legend_*`，而是去 `override.legend.*`。

常见项：

* `override.legend.fontsize`
* `override.legend.title_fontsize`
* `override.legend.handlelength`

### D. 想改线条、marker、颜色

| 目标 | 用什么 |
| --- | --- |
| 当前图是否显示 marker | `figure.marker` |
| 指定各条线的 marker | `figure.markers` |
| 指定各条线的 linestyle | `figure.linestyles` |
| 改当前图颜色顺序 | `figure.override.palette.colors` |
| 改所有线更粗/更细 | `figure.override.lines.linewidth` |
| 改 marker 大小 | `figure.override.lines.markersize` |

例子：

```yaml
figure:
  marker: true
  markers: ["o", "s"]
  linestyles: ["-", "--"]
  override:
    palette.colors: ["#16508F", "#C92D44"]
    lines.linewidth: 1.8
```

### E. 想加额外的辅助元素

| 目标 | 用什么 | 适合图种 |
| --- | --- | --- |
| 加水平或竖直参考线 | `figure.reference_lines` | `line`、`grouped_bar` |
| 加图中文字标注 | `figure.text_annotations` | `line` |
| 给散点直接标注标签 | `figure.annotate_points` + `figure.labels` | `scatter` |
| 给 grouped bar 加显著性标注 | `figure.significance` | `grouped_bar` / `bar` |
| 给热力图显示数字 | `figure.annotate: true` | `heatmap` |
| 给条形图显示条尾数值 | `figure.show_value_labels: true` | `grouped_bar` |

#### `reference_lines` 示例

折线图里：

```yaml
figure:
  reference_lines:
    - y: 0.79
      color: "#D45062"
      linestyle: "--"
      linewidth: 1.0
```

横向 grouped bar 里：

```yaml
figure:
  orientation: horizontal
  reference_lines:
    - x: 10
      color: "#111111"
      linestyle: ":"
```

#### `text_annotations` 示例

```yaml
figure:
  text_annotations:
    - text: Base
      x: 4.8
      y: 67.1
      color: "#2AA6A4"
      fontsize: 7
```

### F. 想改网格、边框、字体、整体尺寸

这些通常应该走 `override`。

| 目标 | 用什么 |
| --- | --- |
| 开关网格 | `override.axes.grid` |
| 网格透明度 | `override.axes.grid_alpha` |
| 网格粗细 | `override.axes.grid_linewidth` |
| 边框颜色 | `override.axes.edgecolor` |
| 坐标轴边框粗细 | `override.axes.linewidth` |
| 刻度长度和粗细 | `override.axes.tick_size` / `override.axes.tick_width` |
| 字体家族 | `override.font.family` |
| 正文字号 | `override.font.size` |
| 标题字号 | `override.font.title_size` |
| 坐标轴标题字号 | `override.font.label_size` |
| tick 字号 | `override.font.tick_size` |
| 图像物理尺寸 | `override.figure.figsize` |

例子：

```yaml
figure:
  override:
    axes.grid: true
    axes.grid_alpha: 0.22
    axes.edgecolor: "#222222"
    font.family: serif
    font.size: 8
    figure.figsize: [9.0, 4.2]
```

---

## 按组件查：不同图种最常用什么字段

### `line.*`

常用字段：

* `x` / `y` / `hue`
* `title` / `xlabel` / `ylabel`
* `legend` / `legend_title` / `legend_bbox_to_anchor` / `legend_ncol`
* `extra_legends`
* `xlim` / `ylim` / `xticks` / `yticks`
* `marker` / `markers` / `linestyles`
* `reference_lines`
* `text_annotations`
* `xformatter` / `yformatter`
* `xscale` / `yscale`

### `scatter.*`

常用字段：

* `x` / `y` / `hue`
* `labels`
* `annotate_points`
* `pareto_frontier`
* `frontier_direction`
* `legend*`
* `alpha`
* `size`

### `bar.*`

常用字段：

* `x` / `y`
* `sort`
* `title`
* `xlabel` / `ylabel`
* `significance`

### `grouped_bar.*`

常用字段：

* `x` / `y` / `hue`
* `legend*`
* `orientation`
* `show_value_labels`
* `value_label_format`
* `reference_lines`
* `significance`
* `xlim` / `ylim`

### `box.*`

常用字段：

* `y`
* `hue`
* `showfliers`
* `legend*`

### `heatmap.*`

常用字段：

* `data.matrix`
* `data.x_labels`
* `data.y_labels`
* `annotate`
* `cmap`

### `subplots.default`

常用字段：

* `nrows`
* `ncols`
* `sharex`
* `sharey`
* `global_legend`
* `legend*`
* `panels`
* `figure_title`
* `figure_note`

### `table_mix.*`

常用字段：

* `elements`
* `row` / `col` / `rowspan` / `colspan`
* `global_legend`
* `legend*`
* `figure_title`
* `figure_note`

---

## 推荐工作流：调图时按什么顺序改

这是最省时间的顺序：

1. 先确定 `paper.profile`、`paper.style` 和 `figure.template`
2. 再把 `data`、`x`、`y`、`hue` 接通
3. 然后只用 `figure` 层先把标题、legend、坐标范围、注释调到位
4. 最后才用 `override` 修视觉细节，比如字号、网格、线宽、尺寸

为什么推荐这样做：

* `figure` 层可读性最好，最容易维护
* 一上来就把东西塞进 `override`，后面往往会忘记“这到底是模板语义还是视觉补丁”

---

## 我该优先查哪里

如果你现在要调图，建议按下面顺序查：

1. 先看这份文档，定位你要改的是“语义参数”还是“样式 token”
2. 再看 [OVERRIDES_cn.md](./OVERRIDES_cn.md) 理解 `override` 的合并逻辑
3. 如果你不确定有哪些内置模板能直接用，再看 [BUILTINS_cn.md](./BUILTINS_cn.md)

---

## 最后给一个最短经验法则

如果你只有 5 秒钟做判断，就用这三条：

* 想改标题、坐标、legend、注释、参考线、panel 布局：写 `figure`
* 想改字体、线宽、网格、配色、图尺寸：写 `override`
* 如果一个参数名字看起来像 Matplotlib token 或 style token，多半就该写到 `override`
