# scifont

**Professional, Reproducible, and Editable Figures for Scientific Publishing.**

`scifont` is a lightweight Python library designed to solve the two most persistent headaches in scientific visualization with Matplotlib:
1.  **Missing Fonts in Docker/Linux**: "Arial" or "Times New Roman" are often missing in CI/CD environments or Linux servers, causing plots to fallback to default fonts.
2.  **Non-Editable Text**: Default Matplotlib settings often export text as paths (shapes), making it impossible to correct typos or adjust formatting in Adobe Illustrator or Inkscape.

## 🚀 Key Features

*   **Bundled Open-Source Fonts**: We ship with **Arimo** and **Tinos** (Apache 2.0 Licensed). These are **metric-compatible** alternatives to Arial and Times New Roman. They are legally safe to distribute and use anywhere.
*   **Metric-Compatible**: Arimo has the exact same character widths and spacing as Arial. Tinos matches Times New Roman. Your layout will remain identical to the proprietary versions.
*   **Editable Vector Graphics**: Automatically configures Matplotlib to export PDFs as `Type 42` objects and SVGs as `<text>` tags. Text remains editable in downstream vector software.
*   **Journal Presets**: One-line configuration for **Nature**, **Science**, **Cell**, and **IEEE** standards.

## 📦 Installation

```bash
pip install scifont
```

*(Or if installing from source)*
```bash
git clone https://github.com/studentiz/scifont.git
cd scifont
pip install .
```

## ⚡ Quick Start

Simply import `scifont` and select your target journal style at the start of your script.

```python
import matplotlib.pyplot as plt
import scifont

# 1. Apply style (e.g., 'nature' for Life Sciences, 'ieee' for Engineering)
scifont.use('nature')

# 2. Plot as usual
plt.figure(figsize=(4, 3))
plt.plot([1, 2, 3], [4, 5, 6], label='Data')

# The font is now Arimo (Arial-compatible)
plt.title("Editable Text in Nature Style")
plt.xlabel("Time (s)")
plt.ylabel("Velocity (m/s)")
plt.legend()

# 3. Save
# The output PDF/SVG will have editable text!
plt.tight_layout()
plt.savefig("figure.pdf")
plt.savefig("figure.svg")
```

## 📖 Supported Journal Styles

`scifont` adjusts font families, sizes, and line widths according to specific journal guidelines (2025 standards).

| Style Argument | Target Font Family | Open-Source Font Used | Base Font Size | Target Journals |
| :--- | :--- | :--- | :--- | :--- |
| `'nature'` | Sans-serif | **Arimo** (matches Arial) | 7 pt | *Nature, Nature Comms, Scientific Reports* |
| `'cell'` | Sans-serif | **Arimo** (matches Arial) | 8 pt | *Cell, Molecular Cell, Neuron* |
| `'science'`| Sans-serif | **Arimo** (matches Arial) | 9 pt | *Science, Science Advances* |
| `'ieee'` | Serif | **Tinos** (matches Times New Roman) | 8 pt | *IEEE Transactions, Phys. Rev. Lett.* |

*Note: You can override any setting (e.g., font size) using standard `plt.rcParams` after calling `scifont.use()`.*

## 🛡️ Why Open Source Fonts? (The Legal Aspect)

Many researchers are unaware that **Arial** and **Times New Roman** are proprietary fonts owned by Monotype.
1.  **Distribution**: It is illegal to bundle `arial.ttf` inside a Python package and distribute it without a costly license.
2.  **Reproducibility**: Reliance on system fonts leads to inconsistencies. A plot rendered on macOS (with Arial) looks different on Ubuntu (without Arial).

**Our Solution:**
We bundle **Arimo** and **Tinos**, developed by Steve Matteson for Google.
*   **License**: **Apache License 2.0**. You can use, bundle, and distribute them freely.
*   **Compatibility**: They are designed to be **Metric-Compatible** with Arial and Times New Roman. This means if you replace Arial with Arimo, the text takes up the *exact same space*. No line breaks will change; no labels will be cut off.

## 🔧 Editable Text (Vector Graphics)

By default, `scifont.use()` applies the following hidden Matplotlib settings to ensure compatibility with Adobe Illustrator, CorelDRAW, and Inkscape:

```python
plt.rcParams['pdf.fonttype'] = 42  # Embbed TrueType fonts (editable)
plt.rcParams['ps.fonttype'] = 42
plt.rcParams['svg.fonttype'] = 'none' # Do not convert text to path
```

## License

The `scifont` code is distributed under the **MIT License**.
The bundled fonts (Arimo and Tinos) are distributed under the **Apache License, Version 2.0**.
