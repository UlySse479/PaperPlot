# PaperPlot

PaperPlot 是一个基于 Matplotlib 的科学绘图框架，旨在生成**论文级别（publication-quality）**的图表，支持统一风格、会议规范（venue-aware）以及可复用的绘图模板。

---

## 当前功能范围

当前仓库已包含：

* profile、style、template 和 plotter 的注册系统
* 内置多种会议（venue）profile 和可视化风格
* 基于模板的绘图支持，包括：

  * 折线图（line）
  * 散点图（scatter）
  * 柱状图（bar）
  * 分组柱状图（grouped bar）
  * 直方图（histogram）
  * 箱线图（box）
  * 热力图（heatmap）
  * 雷达图（radar）
  * 表格（table）
  * 复合布局（composite）
* 支持 JSON/YAML 配置加载及项目本地资源自动加载
* `use_style(...)`：用于已有 Matplotlib 代码的风格统一
* `plot(...)`、`render_template(...)`、`plot_from_config(...)`：Python 端绘图接口
* `managed_figure(...)`：自动管理图像生命周期（避免内存泄漏）
* CLI 工具：支持渲染、校验、资源加载、gallery 生成、注册表查看
* 内置示例 gallery 及视觉回归基线（visual regression baselines）
* smoke / config / CLI / visual regression 测试

---

## 快速示例

```python
from paperplot import plot

data = {
    "epoch": [1, 2, 3, 1, 2, 3],
    "acc": [70, 73, 75, 68, 71, 74],
    "method": ["A", "A", "A", "B", "B", "B"],
}

plot(
    template="line.sota_compare",
    data=data,
    x="epoch",
    y="acc",
    hue="method",
    output="figures/acc.pdf",
)
```

如果你在长时间运行的脚本或 notebook 中保留返回的 figure，请在使用后手动关闭：

```python
import matplotlib.pyplot as plt
from paperplot import plot

fig, ax, spec = plot(
    template="line.sota_compare",
    data=data,
    x="epoch",
    y="acc",
    hue="method",
)

plt.close(fig)
```

如果希望自动管理生命周期，可以使用 `managed_figure(...)`：

```python
from paperplot import managed_figure, plot

with managed_figure(
    plot(
        template="line.sota_compare",
        data=data,
        x="epoch",
        y="acc",
        hue="method",
    )
) as (fig, ax, spec):
    print(ax.get_xlabel())
```

---

## 配置驱动绘图

```python
from paperplot import plot_from_config

config = {
    "paper": {
        "profile": "neurips",
        "style": "academic-bright",
    },
    "figure": {
        "template": "bar.ablation",
        "data": {
            "component": ["base", "w/o aug", "w/o schedule"],
            "score": [82.1, 79.8, 80.4],
        },
        "x": "component",
        "y": "score",
        "output": "figures/ablation.pdf",
    },
}

plot_from_config(config)
```

也支持直接加载文件：

```python
plot_from_config("examples/bar_ablation.yaml")
```

当安装了 `PyYAML` 时将优先使用；否则会使用内置解析器（支持项目所需子集）。

⚠️ 注意：如果你保留返回的 figure，需要手动关闭。

支持的输入：

* Python dict / mapping
* `.json`
* `.yaml` / `.yml`

---

## 科学配色顾问与整篇论文颜色一致性

PaperPlot 现在可以直接复用仓库内 `scientific-color-advisor` 的推荐逻辑，为不同图类型自动选择更适合论文场景的配色，并把同一语义标签在整篇论文中稳定绑定到同一种颜色。

典型用途：

* 折线图、散点图、分组柱状图自动使用更适合论文的分类色板
* 热图自动切到更稳妥的 sequential / diverging 色图
* `Ours`、`Baseline`、`Ablation` 这类标签跨多张图保持颜色不漂移
* 会根据图里的真实系列数量自动推断 `series_count`，避免两条线论文图被分配到过于接近或过于刺眼的颜色

示例配置：

```yaml
paper:
  profile: icml
  style: academic-muted
  color_advisor:
    enabled: true
    usage: manuscript
    tone: restrained
    priorities: [colorblind-safe, grayscale-safe, avoid-red-green]
    namespace: paper-demo
    persist_path: color_advisor/paper-colors.json
    preferred_order: [Ours, Baseline, Ablation]
    bindings:
      Ours: primary
      Baseline: secondary

figure:
  template: line.sota_compare
  data:
    epoch: [1, 2, 3, 1, 2, 3]
    acc: [74.1, 76.8, 78.3, 71.9, 73.5, 74.8]
    method: [Ours, Ours, Ours, Baseline, Baseline, Baseline]
  x: epoch
  y: acc
  hue: method
```

字段含义：

* `enabled`：开启 advisor 驱动的自动推荐
* `usage` / `tone` / `priorities`：控制推荐目标，默认更偏论文安全而不是演示风格
* `namespace`：给一篇论文或一个项目单独建立颜色命名空间
* `persist_path`：把标签到颜色的绑定写入 JSON，分开渲染多张图时也能保持一致
* `preferred_order`：优先把最重要的方法映射到色板前几个位置
* `bindings`：显式把某些标签绑定到 `primary`、`secondary` 或 `color-3` 这类角色

仓库内提供了完整示例：[examples/icml_color_advisor.yaml](/root/PaperPlot/examples/icml_color_advisor.yaml)。

进一步说明建议配合阅读：

* [docs/COLOR_ADVISOR_cn.md](./docs/COLOR_ADVISOR_cn.md)
* [docs/CONFIG_FIELD_GUIDE_cn.md](./docs/CONFIG_FIELD_GUIDE_cn.md)
* [docs/CLI.md](./docs/CLI.md)

---

## 外部资源（Assets）

PaperPlot 支持自动加载项目本地的 profile、style 和 template：

```python
from paperplot import autoload_project_assets

autoload_project_assets(".")
```

支持的目录结构：

* `./paperplot_assets/profiles`
* `./paperplot_assets/styles`
* `./paperplot_assets/templates`
* `./.paperplot/...`
* `./profiles`, `./styles`, `./templates`

支持格式：

* `.json`
* `.yaml` / `.yml`

示例：

```python
from paperplot import autoload_project_assets, plot

autoload_project_assets("examples/assets")

plot(
    template="bar.lab",
    profile="lab",
    visual="lab-muted",
    data={"model": ["A", "B", "C"], "score": [81.2, 83.4, 82.7]},
    x="model",
    y="score",
)
```

---

## 示例配置

部分示例配置文件：

* `scatter_clusters.yaml`
* `heatmap_metrics.yaml`
* `report_layout.yaml`
* `grouped_ablation_significance.yaml`
* `icml_scaling_law.yaml`
* `cvpr_pareto_frontier.yaml`
* `acl_benchmark_matrix.yaml`
* `iclr_benchmark_compare.yaml`
* `cvpr_paper_summary.yaml`

覆盖与重写说明：

* [PaperPlot 图表覆盖与重写指南](./docs/OVERRIDES_cn.md)
* [PaperPlot 配置字段与调图速查手册](./docs/CONFIG_FIELD_GUIDE_cn.md)
* [PaperPlot Color Advisor 使用手册](./docs/COLOR_ADVISOR_cn.md)

---

## 🎯 获奖论文风格模板

近期 ICML / ICLR / ACL / CVPR 的最佳论文中，常见图形模式包括：

* scaling law / compute vs quality 曲线
* Pareto 前沿散点图（带直接标签）
* benchmark 热力图矩阵
* 分组 benchmark 对比
* 表格 + 图表混合布局

PaperPlot 内置对应模板：

* `line.scaling_law`
* `scatter.pareto_frontier`
* `heatmap.benchmark_matrix`
* `grouped_bar.benchmark_compare`
* `table_mix.paper_summary`

---

## 显著性标注（Significance）

支持统计显著性标注：

### 单对比较

```yaml
significance:
  - compare: [A, B]
    text: "*"
```

### 分组消融（对比 baseline）

```yaml
significance:
  - within: each
    against: Base
    text: p<0.05
```

### 更复杂配置

```yaml
significance:
  - within: all
    against: Base
    exclude: [Oracle]
    text: [ns, "**"]
```

---

## CLI

```bash
paperplot render examples/bar_ablation.yaml
paperplot render configs/
paperplot gallery docs/gallery
paperplot assets examples/assets
paperplot validate-config examples/bar_ablation.yaml
paperplot validate-assets examples/assets
paperplot --json list templates
```

核心命令：

* `render`：渲染配置
* `gallery`：生成示例图库
* `assets`：加载并检查资源
* `validate-config`：配置校验
* `validate-assets`：资源校验
* `list`：列出注册项

兼容命令：

* `paperplot validate`（建议改用显式命令）

全局参数：

* `--json`：结构化输出（用于自动化）
* `--quiet`：静默模式

---

## 示例图库

```python
from paperplot import render_gallery

render_gallery("docs/gallery")
```

当前示例包括：

* `line_sota_compare`
* `line_training_curve`
* `bar_ablation`
* `scatter_clusters`
* `box_distribution_compare`
* `heatmap_metrics`
* `report_layout`

---

## 为现有 Matplotlib 代码应用风格

```python
from paperplot import use_style

use_style(profile="icml", visual="academic-muted", size="single")
```

---

## 架构设计

整体架构保持极简：

```text
内置规范 / YAML
        ↓
registry（注册表）
        ↓
resolver（解析器）
        ↓
Matplotlib 渲染器
```

详见：`DESIGN_DOCUMENT.md`

---

## 内置预设

### Profiles

`icml`, `neurips`, `acl`, `cvpr`, `emnlp`, `nature`

### Styles

`default`, `academic-muted`, `academic-bright`, `grayscale-safe`, `nature-clean`

### Templates

包括：

* 折线：`line.*`
* 散点：`scatter.*`
* 柱状：`bar.*`
* 分组柱状：`grouped_bar.*`
* 箱线：`box.*`
* 热力图：`heatmap.*`
* 表格：`table.*`
* 复合：`table_mix.*` 等

---

## 公共 API

### 资源加载

* `autoload_project_assets`
* `load_assets_from_dir`
* `load_profiles_from_dir`
* `load_styles_from_dir`
* `load_templates_from_dir`
* `get_profile`
* `get_style`
* `get_template`

### 注册表查询

* `list_profiles`
* `list_styles`
* `list_templates`
* `list_plotters`

### 注册接口

* `register_profile`
* `register_style`
* `register_template`

### 绘图接口

* `plot`
* `render_template`
* `plot_from_config`
* `render_gallery`
* `use_style`
* `managed_figure`

---

更多内容：

* `docs/CLI.md`：CLI 详细说明与 CI 示例
* `docs/OVERRIDES_cn.md`：override 的合并逻辑与常见改法
* `docs/COLOR_ADVISOR_cn.md`：科研配色推荐与跨论文颜色一致性
