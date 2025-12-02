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

# Cache for font availability checks
_font_availability_cache = {}

def _check_font_available(font_names: list) -> bool:
    """
    Check if any of the specified fonts are available in the system.
    
    Parameters
    ----------
    font_names : list
        List of font names to check (e.g., ['Arial', 'Helvetica'])
    
    Returns
    -------
    bool
        True if at least one font is available, False otherwise
    """
    # Use cache to avoid repeated checks
    cache_key = tuple(sorted(font_names))
    if cache_key in _font_availability_cache:
        return _font_availability_cache[cache_key]
    
    available_fonts = {f.name for f in fm.fontManager.ttflist}
    result = any(font_name in available_fonts for font_name in font_names)
    _font_availability_cache[cache_key] = result
    return result

def _register_bundled_fonts() -> None:
    """
    Scans the internal 'fonts' directory and registers Arimo/Tinos 
    with Matplotlib's font manager dynamically.
    Only registers fonts if they haven't been registered already.
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

    if registered_count > 0:
        logger.debug(f"Registered {registered_count} bundled font(s).")

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
        - 'nature': Sans-serif (Arial/Arimo), 5-7pt (Default for Life Sciences).
        - 'cell': Sans-serif (Arial/Arimo), 6-8pt.
        - 'ieee': Serif (Times New Roman/Tinos), 8pt (Default for Engineering/Physics).
        - 'science': Sans-serif (Arial/Arimo), 7-9pt.
    dpi : int
        Resolution for raster outputs (default: 300).
    """
    # Normalize style string
    style = style.lower().strip()
    
    # 1. Check system fonts and register bundled fonts only if needed
    # For sans-serif styles (nature, cell, science)
    if style in ['nature', 'cell', 'science']:
        system_sans_available = _check_font_available(['Arial', 'Helvetica'])
        if not system_sans_available:
            # System fonts not available, register bundled Arimo
            _register_bundled_fonts()
            logger.info("System fonts (Arial/Helvetica) not found. Using bundled Arimo font.")
        else:
            logger.debug("System fonts (Arial/Helvetica) available. Using system fonts.")
    
    # For serif styles (ieee)
    elif style == 'ieee':
        system_serif_available = _check_font_available(['Times New Roman', 'Times'])
        if not system_serif_available:
            # System fonts not available, register bundled Tinos
            _register_bundled_fonts()
            logger.info("System fonts (Times New Roman/Times) not found. Using bundled Tinos font.")
        else:
            logger.debug("System fonts (Times New Roman/Times) available. Using system fonts.")
    
    # For unknown styles, register bundled fonts as fallback
    else:
        _register_bundled_fonts()
    
    # 2. Ensure Editability
    _configure_vector_output()
    
    # 3. Base Configuration
    rcParams['figure.dpi'] = dpi
    rcParams['savefig.dpi'] = dpi
    rcParams['axes.unicode_minus'] = False  # Use hyphen instead of minus sign glyph

    # 4. Apply Journal-Specific Settings
    if style == 'nature':
        # Nature Guidelines: Sans-serif, 5-7pt.
        # Prioritize system fonts, fallback to Arimo if not available
        rcParams['font.family'] = 'sans-serif'
        if _check_font_available(['Arial', 'Helvetica']):
            rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'Arimo', 'DejaVu Sans']
            font_info = "Arial/Helvetica"
        else:
            rcParams['font.sans-serif'] = ['Arimo', 'DejaVu Sans']
            font_info = "Arimo"
        
        rcParams['font.size'] = 7
        rcParams['axes.labelsize'] = 7
        rcParams['xtick.labelsize'] = 6
        rcParams['ytick.labelsize'] = 6
        rcParams['legend.fontsize'] = 6
        rcParams['axes.linewidth'] = 0.5
        rcParams['grid.linewidth'] = 0.5
        rcParams['lines.linewidth'] = 1.0
        
        logger.info(f"Applied 'Nature' style ({font_info}/Sans-serif, 7pt base).")

    elif style == 'cell':
        # Cell Guidelines: Sans-serif, 6-8pt.
        rcParams['font.family'] = 'sans-serif'
        if _check_font_available(['Arial', 'Helvetica']):
            rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'Arimo', 'DejaVu Sans']
            font_info = "Arial/Helvetica"
        else:
            rcParams['font.sans-serif'] = ['Arimo', 'DejaVu Sans']
            font_info = "Arimo"
        
        rcParams['font.size'] = 8
        rcParams['axes.labelsize'] = 8
        rcParams['xtick.labelsize'] = 7
        rcParams['ytick.labelsize'] = 7
        rcParams['legend.fontsize'] = 7
        rcParams['axes.linewidth'] = 1.0
        
        logger.info(f"Applied 'Cell' style ({font_info}/Sans-serif, 8pt base).")

    elif style == 'science':
        # Science Guidelines: Sans-serif, similar to Nature but slightly larger.
        rcParams['font.family'] = 'sans-serif'
        if _check_font_available(['Arial', 'Helvetica']):
            rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'Arimo', 'DejaVu Sans']
            font_info = "Arial/Helvetica"
        else:
            rcParams['font.sans-serif'] = ['Arimo', 'DejaVu Sans']
            font_info = "Arimo"
        
        rcParams['font.size'] = 8
        rcParams['axes.labelsize'] = 9
        rcParams['xtick.labelsize'] = 8
        rcParams['ytick.labelsize'] = 8
        rcParams['legend.fontsize'] = 8
        
        logger.info(f"Applied 'Science' style ({font_info}/Sans-serif, 8-9pt base).")

    elif style == 'ieee':
        # IEEE Guidelines: Serif (Times), ~8pt.
        rcParams['font.family'] = 'serif'
        if _check_font_available(['Times New Roman', 'Times']):
            rcParams['font.serif'] = ['Times New Roman', 'Times', 'Tinos', 'DejaVu Serif']
            font_info = "Times New Roman/Times"
        else:
            rcParams['font.serif'] = ['Tinos', 'DejaVu Serif']
            font_info = "Tinos"
        
        rcParams['font.size'] = 8
        rcParams['axes.labelsize'] = 8
        rcParams['xtick.labelsize'] = 8
        rcParams['ytick.labelsize'] = 8
        rcParams['legend.fontsize'] = 8
        
        # IEEE figures often look better with grid
        rcParams['axes.grid'] = True
        rcParams['grid.alpha'] = 0.4
        rcParams['grid.linestyle'] = '--'
        
        logger.info(f"Applied 'IEEE' style ({font_info}/Serif, 8pt base).")

    else:
        # Default fallback
        rcParams['font.family'] = 'sans-serif'
        if _check_font_available(['Arial', 'Helvetica']):
            rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'Arimo', 'sans-serif']
        else:
            rcParams['font.sans-serif'] = ['Arimo', 'sans-serif']
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