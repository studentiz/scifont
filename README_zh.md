# scifont

**[English](README.md) | [中文](README_zh.md)**

**让 Matplotlib 图表支持可编辑文本，并符合期刊字体要求。**

## 问题

作为科研人员，你在制作发表图表时很可能遇到过这些问题：

1. **不同环境下字体不一致**：在你的本地电脑（Windows、macOS 或 Linux）上画出来的图很完美，但在服务器、Docker 容器或 CI/CD 流水线中运行时，字体就缺失了。Arial 和 Times New Roman 不是所有环境都有，导致图表出问题或看起来不一样。

2. **矢量图形软件中文本无法编辑**：你把图导出为 PDF 或 SVG，准备在 Adobe Illustrator 或 Inkscape 里做最后编辑，结果发现文本被转换成了不可编辑的路径。想改个错别字或调整标签，就得重新画整个图。

3. **手动配置期刊样式太麻烦**：每个期刊都有特定的字体和字号要求。你花几个小时调 Matplotlib 的 `rcParams` 来匹配 Nature 的要求，投稿到 Science 或 IEEE 时又要全部重来一遍。

4. **中文显示问题**：在图表中使用中文时，如果使用期刊推荐的英文字体（如 Arial、Times New Roman），中文部分会显示为"口口口"或方块，因为这些字体不支持中文字符。

## 解决方案

`scifont` 用一行代码解决这三个问题：

```python
import scifont
scifont.use('nature')  # 搞定！
```

**它能做什么：**
- ✅ 系统有字体（Arial、Helvetica、Times New Roman）就用系统的，没有就无缝切换到兼容的开源字体（Arimo/Tinos）
- ✅ 配置 Matplotlib 导出可编辑的文本到 PDF/SVG 文件，在 Adobe Illustrator 里改错别字不用重画
- ✅ 一行代码搞定 Nature、Science、Cell、IEEE 等期刊的样式要求——再也不用手动调 `rcParams` 了
- ✅ 支持中文显示：使用 `scifont.use('zh')` 自动使用系统中可用的中文字体，确保中文和英文都能正确显示

## 🚀 核心功能

*   **智能字体选择**：系统有 Arial、Helvetica、Times New Roman 就用系统的，没有就自动用打包的开源字体（Arimo、Tinos）。

*   **度量兼容字体**：我们打包了 **Arimo** 和 **Tinos**（Apache 2.0 许可）作为 Arial 和 Times New Roman 的替代品。字符宽度和间距完全一样，所以布局不会变。

*   **可编辑矢量图形**：自动配置 Matplotlib 把 PDF 导出为 `Type 42` 格式，SVG 导出为 `<text>` 标签。文本在 Adobe Illustrator、Inkscape、CorelDRAW 里都能编辑。

*   **期刊预设**：一行代码配置 **Nature**、**Science**、**Cell**、**IEEE** 等期刊的标准样式。

*   **发表级样式美化**：自动应用科学论文发表的最佳实践，包括向内刻度、合适的线条宽度和简洁的坐标轴样式，让图表更专业。

## 📦 安装

```bash
pip install --upgrade scifont
```

或者从源码安装：
```bash
git clone https://github.com/studentiz/scifont.git
cd scifont
pip install .
```

## ⚡ 快速开始

### 英文图表（期刊样式）

```python
import matplotlib.pyplot as plt
import scifont

# 应用期刊样式
scifont.use('nature')

# 正常画图
plt.figure(figsize=(4, 3))
plt.plot([1, 2, 3], [4, 5, 6], label='Data')
plt.title("Editable Text in Nature Style")
plt.xlabel("Time (s)")
plt.ylabel("Velocity (m/s)")
plt.legend()

# 保存 - 文本在 Adobe Illustrator 里可以编辑！
plt.tight_layout()
plt.savefig("figure.pdf")
plt.savefig("figure.svg")
```

### 中文图表

如果你的图表中包含中文内容，使用 `'zh'` 样式可以确保中文正确显示：

```python
import matplotlib.pyplot as plt
import scifont

# 使用中文字体样式
scifont.use('zh')

# 正常画图，可以包含中文
plt.figure(figsize=(4, 3))
plt.plot([1, 2, 3], [4, 5, 6], label='数据')
plt.title("示例图表")
plt.xlabel("时间 (秒)")
plt.ylabel("速度 (米/秒)")
plt.legend()

# 保存 - 中文和英文都能正确显示！
plt.tight_layout()
plt.savefig("figure.pdf")
plt.savefig("figure.svg")
```

`scifont.use('zh')` 会自动检测系统中可用的中文字体（如 Microsoft YaHei、PingFang SC、Noto Sans CJK SC 等），并将其设置为主要字体。由于大多数中文字体也支持英文，所以英文和中文都能正确显示。

## 📖 支持的期刊样式

| 样式 | 字体系列 | 主要字体 | 备用字体 | 基础字号 | 目标期刊 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `'nature'` | 无衬线 | Arial/Helvetica | Arimo | 7 pt | Nature, Nature Comms, Scientific Reports |
| `'cell'` | 无衬线 | Arial/Helvetica | Arimo | 8 pt | Cell, Molecular Cell, Neuron |
| `'science'`| 无衬线 | Arial/Helvetica | Arimo | 8 pt | Science, Science Advances |
| `'ieee'` | 衬线 | Times New Roman/Times | Tinos | 8 pt | IEEE Transactions, Phys. Rev. Lett. |
| `'zh'` | 无衬线 | 系统可用中文字体 | DejaVu Sans | 8 pt | 包含中文内容的图表 |

*注意：`'zh'` 样式会自动检测系统中可用的中文字体（如 Microsoft YaHei、PingFang SC、Noto Sans CJK SC 等）。如果系统中没有中文字体，会给出警告并使用 DejaVu Sans 作为回退。*

*注意：调用 `scifont.use()` 后，你仍然可以用 `plt.rcParams` 覆盖任何设置。*

## 🎯 scifont 能做什么（以及不能做什么）

**scifont 解决的问题：**
- ✅ 所有平台（Windows、macOS、Linux）和环境（本地电脑、服务器、Docker 容器）下的字体一致性
- ✅ PDF/SVG 文件中的文本可编辑——在 Adobe Illustrator 里改错别字不用重画
- ✅ 符合主要期刊要求的字体和字号设置
- ✅ 真正的跨平台兼容——同样的代码在任何地方都能用
- ✅ 专业的图表样式美化——自动配置刻度、边框和线条宽度，让图表达到发表级别的外观

**scifont 不能解决的问题：**
- ❌ 它不是设计工具——你还是需要调整布局、颜色和样式
- ❌ 它不会自动让你的图表达到发表级别——你还是需要微调间距、图例和注释
- ❌ 它只是配置助手，不能替代手动工作

把它当成一个坚实的基础。一个 `scifont.use('nature')` 调用可以替代几十个手动 `rcParams` 调整，但你仍然可以完全控制后续的所有自定义。

## 🛡️ 为什么打包开源字体？

**Arial** 和 **Times New Roman** 是 Monotype 公司的专有字体。在没有昂贵许可证的情况下，把它们打包到 Python 包里分发是违法的。而且，只依赖系统字体会导致不一致——在 Windows 或 macOS（有 Arial）上渲染的图和在 Linux 服务器或 Docker 容器（没有 Arial）上看起来不一样。

**我们的解决方案：** 我们打包了 **Arimo** 和 **Tinos**（由 Steve Matteson 为 Google 开发）作为备用字体。它们：
- **Apache License 2.0**：可以自由使用、打包和分发
- **度量兼容**：字符宽度和间距与 Arial 和 Times New Roman 完全一样。换字体时布局不会变。

## 🔧 技术细节

默认情况下，`scifont.use()` 会应用这些 Matplotlib 设置：

```python
plt.rcParams['pdf.fonttype'] = 42  # 嵌入 TrueType 字体（可编辑）
plt.rcParams['ps.fonttype'] = 42
plt.rcParams['svg.fonttype'] = 'none'  # 不要把文本转成路径
```

这确保了与 Adobe Illustrator、CorelDRAW 和 Inkscape 的兼容性。

## 许可证

`scifont` 代码在 **MIT 许可证**下分发。  
打包的字体（Arimo 和 Tinos）在 **Apache License, Version 2.0** 下分发。
