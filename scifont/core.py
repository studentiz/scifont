"""
Core functionality for scifont.
Handles font loading and matplotlib configuration management.
"""

import logging
from pathlib import Path

import matplotlib.font_manager as fm
from matplotlib import rcParams

# Configure logging
logging.basicConfig(level=logging.INFO, format="[scifont] %(message)s")
logger = logging.getLogger(__name__)

# Constants
PACKAGE_DIR = Path(__file__).parent
FONT_DIR = PACKAGE_DIR / "fonts"

def _register_bundled_fonts() -> None:
    """
    Scans the internal 'fonts' directory and registers Arimo/Tinos 
    with Matplotlib's font manager dynamically.
    """
    if not FONT_DIR.exists():
        logger.error(f"Font directory not found: {FONT_DIR}")
        return

    registered_count = 0
    for font_path in FONT_DIR.glob("*.ttf"):
        try:
            fm.fontManager.addfont(str(font_path))
            registered_count += 1
        except Exception as e:
            logger.warning(f"Failed to load font {font_path.name}: {e}")

    # Verify if Arimo/Tinos are actually available now
    # This is a silent check to ensure logic validity
    available_fonts = {f.name for f in fm.fontManager.ttflist}
    if "Arimo" not in available_fonts and "Tinos" not in available_fonts:
        logger.warning("Bundled fonts (Arimo/Tinos) were not registered correctly.")

def _configure_vector_output() -> None:
    """
    Forces Matplotlib to output text as editable objects (Type 42) 
    instead of outlines (Type 3) for PDF/PS, and preserves text tags for SVG.
    """
    # PDF/PS: Use TrueType (Type 42) to ensure text remains editable in Illustrator
    rcParams['pdf.fonttype'] = 42
    rcParams['ps.fonttype'] = 42
    
    # SVG: Do not convert text to paths
    rcParams['svg.fonttype'] = 'none'

def use(style: str = 'nature', dpi: int = 300) -> None:
    """
    Apply a specific scientific publication style to Matplotlib.

    Parameters
    ----------
    style : str
        The target journal style. Options:
        - 'nature': Sans-serif (Arimo), 5-7pt (Default for Life Sciences).
        - 'cell': Sans-serif (Arimo), 6-8pt.
        - 'ieee': Serif (Tinos), 8pt (Default for Engineering/Physics).
        - 'science': Sans-serif (Arimo), 7-9pt.
    dpi : int
        Resolution for raster outputs (default: 300).
    """
    # 1. Load Fonts
    _register_bundled_fonts()
    
    # 2. Ensure Editability
    _configure_vector_output()
    
    # 3. Base Configuration
    rcParams['figure.dpi'] = dpi
    rcParams['savefig.dpi'] = dpi
    rcParams['axes.unicode_minus'] = False  # Use hyphen instead of minus sign glyph
    
    # Normalize style string
    style = style.lower().strip()

    # 4. Apply Journal-Specific Settings
    if style == 'nature':
        # Nature Guidelines: Sans-serif, 5-7pt.
        rcParams['font.family'] = 'sans-serif'
        rcParams['font.sans-serif'] = ['Arimo', 'Arial', 'Helvetica', 'DejaVu Sans']
        
        rcParams['font.size'] = 7
        rcParams['axes.labelsize'] = 7
        rcParams['xtick.labelsize'] = 6
        rcParams['ytick.labelsize'] = 6
        rcParams['legend.fontsize'] = 6
        rcParams['axes.linewidth'] = 0.5
        rcParams['grid.linewidth'] = 0.5
        rcParams['lines.linewidth'] = 1.0
        
        logger.info("Applied 'Nature' style (Arimo/Sans-serif, 7pt base).")

    elif style == 'cell':
        # Cell Guidelines: Sans-serif, 6-8pt.
        rcParams['font.family'] = 'sans-serif'
        rcParams['font.sans-serif'] = ['Arimo', 'Arial', 'Helvetica', 'DejaVu Sans']
        
        rcParams['font.size'] = 8
        rcParams['axes.labelsize'] = 8
        rcParams['xtick.labelsize'] = 7
        rcParams['ytick.labelsize'] = 7
        rcParams['legend.fontsize'] = 7
        rcParams['axes.linewidth'] = 1.0
        
        logger.info("Applied 'Cell' style (Arimo/Sans-serif, 8pt base).")

    elif style == 'science':
        # Science Guidelines: Sans-serif, similar to Nature but slightly larger.
        rcParams['font.family'] = 'sans-serif'
        rcParams['font.sans-serif'] = ['Arimo', 'Arial', 'Helvetica', 'DejaVu Sans']
        
        rcParams['font.size'] = 8
        rcParams['axes.labelsize'] = 9
        rcParams['xtick.labelsize'] = 8
        rcParams['ytick.labelsize'] = 8
        rcParams['legend.fontsize'] = 8
        
        logger.info("Applied 'Science' style (Arimo/Sans-serif, 8-9pt base).")

    elif style == 'ieee':
        # IEEE Guidelines: Serif (Times), ~8pt.
        rcParams['font.family'] = 'serif'
        rcParams['font.serif'] = ['Tinos', 'Times New Roman', 'Times', 'DejaVu Serif']
        
        rcParams['font.size'] = 8
        rcParams['axes.labelsize'] = 8
        rcParams['xtick.labelsize'] = 8
        rcParams['ytick.labelsize'] = 8
        rcParams['legend.fontsize'] = 8
        
        # IEEE figures often look better with grid
        rcParams['axes.grid'] = True
        rcParams['grid.alpha'] = 0.4
        rcParams['grid.linestyle'] = '--'
        
        logger.info("Applied 'IEEE' style (Tinos/Serif, 8pt base).")

    else:
        # Default fallback
        rcParams['font.family'] = 'sans-serif'
        rcParams['font.sans-serif'] = ['Arimo', 'Arial', 'sans-serif']
        logger.warning(f"Unknown style '{style}'. Loaded fonts but defaulted to basic settings.")

def get_style_info() -> dict:
    """Returns the current active font settings for debugging."""
    info = {
        "font.family": rcParams.get('font.family', 'unknown'),
        "pdf.fonttype": rcParams.get('pdf.fonttype', 'unknown'),
        "font.size": rcParams.get('font.size', 'unknown')
    }
    
    # Safely get font lists
    sans_serif = rcParams.get('font.sans-serif', [])
    serif = rcParams.get('font.serif', [])
    
    if isinstance(sans_serif, list) and len(sans_serif) > 0:
        info["font.sans-serif"] = sans_serif[:3]
    else:
        info["font.sans-serif"] = []
    
    if isinstance(serif, list) and len(serif) > 0:
        info["font.serif"] = serif[:3]
    else:
        info["font.serif"] = []
    
    return info