# scifont

**[中文](README_zh.md) | [English](README.md)**

**Publication-ready Matplotlib figures with editable text and journal-compliant fonts.**

## The Problem

As a researcher creating figures for publication, you've likely encountered these issues:

1. **Font inconsistencies across environments**: Your figures look perfect on your local machine (Windows, macOS, or Linux), but when you run the same code on a server, in a Docker container, or in CI/CD pipelines, the fonts are missing. Arial and Times New Roman aren't available everywhere, causing your figures to break or look different.

2. **Uneditable text in vector graphics software**: You export your figure as PDF or SVG for final editing in Adobe Illustrator or Inkscape, only to discover that the text is converted to uneditable paths. Fixing a typo or adjusting labels means redrawing the entire figure.

3. **Manual journal style configuration**: Each journal has specific font and size requirements. You spend hours tweaking Matplotlib's `rcParams` to match Nature's guidelines, then repeat the entire process when submitting to Science or IEEE.

## The Solution

`scifont` solves all three problems with one line of code:

```python
import scifont
scifont.use('nature')  # That's it!
```

**What it does:**
- ✅ Automatically uses system fonts (Arial, Helvetica, Times New Roman) when available, seamlessly falls back to metric-compatible open-source fonts (Arimo/Tinos) when system fonts are missing
- ✅ Configures Matplotlib to export editable text in PDF/SVG files, so you can fix typos in Adobe Illustrator without redrawing
- ✅ Provides one-line configuration for Nature, Science, Cell, and IEEE style guidelines—no more manual `rcParams` tweaking

## 🚀 Key Features

*   **Smart Font Selection**: Prioritizes system fonts (Arial, Helvetica, Times New Roman) when available. Automatically falls back to bundled open-source fonts (Arimo, Tinos) when system fonts are missing.

*   **Metric-Compatible Fonts**: We bundle **Arimo** and **Tinos** (Apache 2.0 Licensed) as alternatives to Arial and Times New Roman. They have identical character widths and spacing, so your layout stays exactly the same.

*   **Editable Vector Graphics**: Automatically configures Matplotlib to export PDFs as `Type 42` objects and SVGs as `<text>` tags. Text remains editable in Adobe Illustrator, Inkscape, and CorelDRAW.

*   **Journal Presets**: One-line configuration for **Nature**, **Science**, **Cell**, and **IEEE** standards.

## 📦 Installation

```bash
pip install --upgrade scifont
```

Or install from source:
```bash
git clone https://github.com/studentiz/scifont.git
cd scifont
pip install .
```

## ⚡ Quick Start

```python
import matplotlib.pyplot as plt
import scifont

# Apply journal style
scifont.use('nature')

# Plot as usual
plt.figure(figsize=(4, 3))
plt.plot([1, 2, 3], [4, 5, 6], label='Data')
plt.title("Editable Text in Nature Style")
plt.xlabel("Time (s)")
plt.ylabel("Velocity (m/s)")
plt.legend()

# Save - text will be editable in Adobe Illustrator!
plt.tight_layout()
plt.savefig("figure.pdf")
plt.savefig("figure.svg")
```

## 📖 Supported Journal Styles

| Style | Font Family | Primary Font | Fallback Font | Base Size | Target Journals |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `'nature'` | Sans-serif | Arial/Helvetica | Arimo | 7 pt | Nature, Nature Comms, Scientific Reports |
| `'cell'` | Sans-serif | Arial/Helvetica | Arimo | 8 pt | Cell, Molecular Cell, Neuron |
| `'science'`| Sans-serif | Arial/Helvetica | Arimo | 8 pt | Science, Science Advances |
| `'ieee'` | Serif | Times New Roman/Times | Tinos | 8 pt | IEEE Transactions, Phys. Rev. Lett. |

*Note: You can override any setting using `plt.rcParams` after calling `scifont.use()`.*

## 🎯 What scifont Does (and Doesn't Do)

**What scifont solves:**
- ✅ Font consistency across all platforms (Windows, macOS, Linux) and environments (local machines, servers, Docker containers)
- ✅ Editable text in PDF/SVG files—fix typos in Adobe Illustrator without redrawing
- ✅ Journal-compliant font and size settings for major journals
- ✅ True cross-platform compatibility—same code works everywhere

**What scifont doesn't do:**
- ❌ It's not a design tool—you still need to adjust layout, colors, and aesthetics
- ❌ It won't automatically make your figures publication-ready—you'll still need to fine-tune spacing, legends, and annotations
- ❌ It's a configuration helper, not a replacement for manual work

Think of it as a solid foundation. One `scifont.use('nature')` call replaces dozens of manual `rcParams` tweaks, but you're still in full control to customize everything afterward.

## 🛡️ Why Bundle Open-Source Fonts?

**Arial** and **Times New Roman** are proprietary fonts owned by Monotype. It's illegal to bundle them in a Python package without a costly license. Also, relying on system fonts alone causes inconsistencies—a plot rendered on Windows or macOS (with Arial) looks different on Linux servers or Docker containers (without Arial).

**Our solution:** We bundle **Arimo** and **Tinos** (developed by Steve Matteson for Google) as fallback fonts. They're:
- **Apache License 2.0**: Free to use, bundle, and distribute
- **Metric-compatible**: Identical character widths and spacing to Arial and Times New Roman. No layout changes when switching fonts.

## 🔧 Technical Details

By default, `scifont.use()` applies these Matplotlib settings:

```python
plt.rcParams['pdf.fonttype'] = 42  # Embed TrueType fonts (editable)
plt.rcParams['ps.fonttype'] = 42
plt.rcParams['svg.fonttype'] = 'none'  # Don't convert text to paths
```

This ensures compatibility with Adobe Illustrator, CorelDRAW, and Inkscape.

## License

The `scifont` code is distributed under the **MIT License**.  
The bundled fonts (Arimo and Tinos) are distributed under the **Apache License, Version 2.0**.
