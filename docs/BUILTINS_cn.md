# PaperPlot 内置 Profiles、Styles 与 Templates 说明

这份文档用于快速理解 PaperPlot 当前所有内置 `profiles`、`styles` 和 `templates`。它不是 API 参考，而是偏“选型手册”：每个内置元素都说明它更适合什么场景、默认强化了什么行为，以及和其他内置项相比最关键的差异。

如果需要重新生成本文使用的图片，可以在仓库根目录执行：

```bash
python scripts/render_builtin_catalog_assets.py
```

## 怎么选

通常可以按下面这个顺序选：

1. 先选 `profile`：决定论文版芯尺寸、字体家族、字号和默认导出规格。
2. 再选 `style`：决定颜色、网格、线宽和图例气质。
3. 最后选 `template`：决定图形类型、默认布局和针对特定论文场景的偏置。

一个简单心智模型：

* `profile` 解决“像不像这个 venue 的版式”
* `style` 解决“图看起来是什么视觉语言”
* `template` 解决“这张图应该按什么结构表达”

## 内置 Profiles

所有 profile 都默认导出 `pdf` 和 `png`，默认 `dpi=300`，并使用 `bbox_inches="tight"`。真正拉开差异的是字体和尺寸 token。

| 名称 | 特点 | 单栏 / 双栏 / 方图尺寸（英寸） | 预览 |
| --- | --- | --- | --- |
| `acl` | 偏传统 NLP 论文版式，衬线字体，字号略大于 ICML/NeurIPS，适合正文密度稍高但仍希望图中文字稳妥可读的场景。 | `3.3×2.3` / `6.9×3.1` / `3.1×3.1` | ![acl](./builtins/profiles/profile_acl.png) |
| `cvpr` | 视觉论文常用的紧凑单栏比例，衬线字体，图面较精炼，适合视觉 benchmark、Pareto、SOTA 对比。 | `3.25×2.25` / `6.75×3.05` / `3.15×3.15` | ![cvpr](./builtins/profiles/profile_cvpr.png) |
| `emnlp` | 和 ACL 相近，适合 NLP/LLM 论文中的结果图、消融图和表格混排。 | `3.3×2.3` / `6.9×3.1` / `3.1×3.1` | ![emnlp](./builtins/profiles/profile_emnlp.png) |
| `icml` | 当前最稳妥的通用研究型 profile 之一，衬线字体、单栏高度略紧凑，适合训练曲线、scaling law 和大多数实验结果图。 | `3.25×2.2` / `6.8×3.0` / `3.0×3.0` | ![icml](./builtins/profiles/profile_icml.png) |
| `nature` | 唯一的无衬线 profile，字号更小、图面更克制，适合希望整体更现代、更简洁、更像期刊 figure 的场景。 | `3.5×2.4` / `7.2×3.2` / `3.2×3.2` | ![nature](./builtins/profiles/profile_nature.png) |
| `neurips` | 单栏尺寸最紧凑，适合信息密度高、版面很紧、但仍想保持 conference-style 规范感的图。 | `3.2×2.1` / `6.7×3.0` / `3.1×3.1` | ![neurips](./builtins/profiles/profile_neurips.png) |

### Profile 选择建议

* 做 NLP / LLM 论文，优先从 `acl`、`emnlp`、`icml` 开始。
* 做 vision 或希望图面更紧凑，优先看 `cvpr`。
* 做期刊图或想要更 clean 的无衬线版式，优先看 `nature`。
* 版面极紧、图很多时，`neurips` 往往更省空间。

## 内置 Styles

style 主要决定配色、网格、线条粗细、marker 大小和 legend 气质。它不会改变 figure 结构，但会明显影响“论文感”和是否耐打印。

| 名称 | 特点 | 适合场景 | 预览 |
| --- | --- | --- | --- |
| `default` | 最基础的 PaperPlot 风格，不开网格，轴线和刻度比较明确，颜色直接，适合作为二次定制起点。 | 自定义风格前的基础底板 | ![default](./builtins/styles/style_default.png) |
| `academic-muted` | 低饱和学术配色，轻网格，线宽略加粗，整体最稳妥、最通用。 | 大多数论文主图、训练曲线、benchmark 对比 | ![academic-muted](./builtins/styles/style_academic_muted.png) |
| `academic-bright` | 更高对比、更鲜明的类别色，marker 更大，适合想突出系列差异的图。 | 消融、分组对比、多方法并列图 | ![academic-bright](./builtins/styles/style_academic_bright.png) |
| `grayscale-safe` | 使用灰阶调色板并保留结构性区分，强调打印和审稿场景下的可辨识性。 | 黑白打印、补充材料、对可访问性要求高的论文 | ![grayscale-safe](./builtins/styles/style_grayscale_safe.png) |
| `nature-clean` | 更克制的 clean 风格，弱化网格，线条与图例都更简洁，整体更像期刊插图。 | 期刊风格图、结果摘要图、表图混排 | ![nature-clean](./builtins/styles/style_nature_clean.png) |

### Style 选择建议

* 不确定时，先用 `academic-muted`。
* 需要明显拉开方法区分时，用 `academic-bright`。
* 需要灰度安全或担心打印后坍塌时，用 `grayscale-safe`。
* 想让图更干净、更像期刊摘要图时，用 `nature-clean`。

## 内置 Templates

template 决定默认图种、常用参数和某些任务导向的默认行为。下面按图形家族来整理。

### Line

| 名称 | 图形特点 | 适合场景 | 预览 |
| --- | --- | --- | --- |
| `line.default` | 通用折线模板，默认启用 marker、提供多种 marker 和 linestyle。 | 任意时间序列、步数曲线、趋势图 | ![line.default](./builtins/templates/line_default.png) |
| `line.scaling_law` | 基于 `line.default`，默认标题与图例位置更适合 scaling-law 类展示。 | 参数量、tokens、compute 与 loss/score 的关系 | ![line.scaling_law](./builtins/templates/line_scaling_law.png) |
| `line.sota_compare` | 面向多方法性能比较，默认更偏“结果对比图”而不是训练过程图。 | SOTA 对比、budget-performance 曲线 | ![line.sota_compare](./builtins/templates/line_sota_compare.png) |
| `line.training_curve` | 基于 `line.default`，默认关闭 marker，让连续训练轨迹更干净。 | train/val 曲线、收敛过程、迭代稳定性 | ![line.training_curve](./builtins/templates/line_training_curve.png) |

### Scatter

| 名称 | 图形特点 | 适合场景 | 预览 |
| --- | --- | --- | --- |
| `scatter.default` | 通用散点模板，默认半透明、固定点大小，并支持按类别区分 marker。 | 嵌入分布、簇分离、二维投影 | ![scatter.default](./builtins/templates/scatter_default.png) |
| `scatter.pareto_frontier` | 自动注释点并绘制 Pareto 前沿，是最典型的“论文摘要图”之一。 | 速度-效果、延迟-精度、成本-收益权衡 | ![scatter.pareto_frontier](./builtins/templates/scatter_pareto_frontier.png) |

### Bar

| 名称 | 图形特点 | 适合场景 | 预览 |
| --- | --- | --- | --- |
| `bar.default` | 基础柱状图模板，默认不排序。 | 单指标类别比较 | ![bar.default](./builtins/templates/bar_default.png) |
| `bar.ablation` | 基于 `bar.default`，默认按数值排序，更像论文里的消融结果图。 | 组件消融、模块移除、策略对比 | ![bar.ablation](./builtins/templates/bar_ablation.png) |
| `grouped_bar.default` | 分组柱状图模板，默认 `bar_width=0.22` 并保留 legend。 | 多 setting、多模型、多数据集并列比较 | ![grouped_bar.default](./builtins/templates/grouped_bar_default.png) |
| `grouped_bar.benchmark_compare` | 在 `grouped_bar.default` 上进一步偏向 benchmark 对比，默认标题和 legend 位置更适合正式结果图。 | 多 benchmark 上的基线 vs 方法对比 | ![grouped_bar.benchmark_compare](./builtins/templates/grouped_bar_benchmark_compare.png) |
| `ablation.study` | 基于 `grouped_bar.default`，专门面向 grouped ablation，配合显著性标注更自然。 | 同类组件的 base/remove、多因素消融对照 | ![ablation.study](./builtins/templates/ablation_study.png) |

### Distribution

| 名称 | 图形特点 | 适合场景 | 预览 |
| --- | --- | --- | --- |
| `hist.default` | 直方图模板，默认 `bins=20`，适合快速看单变量分布。 | 误差分布、长度分布、响应统计 | ![hist.default](./builtins/templates/hist_default.png) |
| `box.default` | 箱线图模板，默认不显示离群点，图面更干净。 | 方法分布稳健性比较 | ![box.default](./builtins/templates/box_default.png) |
| `box.distribution_compare` | 基于 `box.default`，更明确地面向多方法分布对照。 | 多模型方差、稳定性、跨 seed 分布比较 | ![box.distribution_compare](./builtins/templates/box_distribution_compare.png) |

### Matrix And Summary

| 名称 | 图形特点 | 适合场景 | 预览 |
| --- | --- | --- | --- |
| `heatmap.default` | 基础热力图模板，默认不注释数值。 | 相似度矩阵、错误矩阵、任意二维数值表 | ![heatmap.default](./builtins/templates/heatmap_default.png) |
| `heatmap.benchmark_matrix` | 默认开启数值注释并采用更常见的 benchmark heatmap 配置。 | 数据集 × 语言、任务 × 模型、指标矩阵 | ![heatmap.benchmark_matrix](./builtins/templates/heatmap_benchmark_matrix.png) |
| `radar.default` | 方图尺寸的雷达图模板，默认范围 `[0, 1]`。 | 少量指标的概括性对比，不适合精确读数场景 | ![radar.default](./builtins/templates/radar_default.png) |
| `table.default` | 基础表格模板，单栏内输出稳定。 | 小型结果表、方法摘要表 | ![table.default](./builtins/templates/table_default.png) |

### Composite Layout

| 名称 | 图形特点 | 适合场景 | 预览 |
| --- | --- | --- | --- |
| `subplots.default` | 多 panel 模板，默认自动 panel label，适合做 A/B/C/D 式论文组合图。 | 多图并排、主结果 + 分析图 | ![subplots.default](./builtins/templates/subplots_default.png) |
| `table_mix.default` | 表格和图形混合布局模板，默认双栏并给右侧图更多宽度。 | 左表右图、摘要结果 + 解释图 | ![table_mix.default](./builtins/templates/table_mix_default.png) |
| `table_mix.paper_summary` | 基于 `table_mix.default`，更明确面向“论文主结果摘要”的混合布局。 | 首页主图、paper teaser、summary figure | ![table_mix.paper_summary](./builtins/templates/table_mix_paper_summary.png) |

## 推荐组合

下面给几个比较稳妥的起手组合：

| 使用目标 | 推荐组合 | 原因 |
| --- | --- | --- |
| 通用 ML 论文主图 | `icml` + `academic-muted` + 对应任务模板 | 最稳、最不容易过度设计 |
| 视觉论文 benchmark 图 | `cvpr` + `grayscale-safe` + `line.sota_compare` / `scatter.pareto_frontier` | 结构区分强，打印更稳 |
| NLP/LLM 实验图 | `acl` 或 `emnlp` + `academic-muted` + `grouped_bar.benchmark_compare` / `heatmap.benchmark_matrix` | 版式匹配常见 conference 习惯 |
| 期刊摘要图 | `nature` + `nature-clean` + `table_mix.paper_summary` | 更 clean，更适合摘要式表达 |
| 消融章节 | `neurips` + `academic-bright` + `bar.ablation` / `ablation.study` | 紧凑且层次清楚 |

## 列表查询

如果你只想在命令行快速查看当前内置注册项，也可以直接运行：

```bash
paperplot list profiles
paperplot list styles
paperplot list templates
```

或者用 JSON 输出：

```bash
paperplot --json list all
```
