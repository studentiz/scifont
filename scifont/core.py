"""
Core functionality for scifont.
Handles font loading and matplotlib configuration management.
"""

import logging
from pathlib import Path

import matplotlib.font_manager as fm
from matplotlib import rcParams

# Configure logging for scifont
# Only show INFO and above, suppress DEBUG messages
# Use force=True to override any existing configuration
logging.basicConfig(
    level=logging.WARNING,  # Set root logger to WARNING to suppress most messages
    format="[scifont] %(message)s",
    force=True
)

# Configure our specific logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Remove any existing handlers to avoid duplicates
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[scifont] %(message)s"))
    logger.addHandler(handler)
logger.propagate = False  # Don't propagate to root logger to avoid double output

# Suppress Matplotlib and fontTools loggers completely
# These messages come from fontTools during PDF generation and are not useful
# The font subsetting messages (like "maxp pruned", "cmap pruned") are debug info
for logger_name in ['matplotlib', 'fontTools', 'fontTools.subset', 'fontTools.ttLib', 
                    'matplotlib.font_manager', 'matplotlib.backends.backend_pdf']:
    try:
        other_logger = logging.getLogger(logger_name)
        other_logger.setLevel(logging.ERROR)  # Only show ERROR level
        other_logger.propagate = False  # Don't propagate to root
        # Remove handlers to prevent output
        other_logger.handlers = []
    except Exception:
        pass

# Constants
PACKAGE_DIR = Path(__file__).parent
FONT_DIR = PACKAGE_DIR / "fonts"

# Cache for font availability checks
_font_availability_cache = {}
# Track registered bundled fonts to avoid duplicate registration
_registered_bundled_fonts = set()

def _clear_font_cache() -> None:
    """Clear font availability cache when fonts are registered."""
    _font_availability_cache.clear()

def _get_chinese_fonts() -> list:
    """
    Get a list of Chinese fonts available on the system.
    Returns fonts in order of preference for each platform.
    
    Returns
    -------
    list
        List of Chinese font names that are available on the system.
        Returns empty list if no Chinese fonts are found.
    """
    # Common Chinese fonts by platform
    # Order matters: check most preferred fonts first
    chinese_font_candidates = [
        # Windows
        'Microsoft YaHei',      # 微软雅黑 (most common on Windows)
        'SimHei',              # 黑体
        'SimSun',              # 宋体
        'KaiTi',               # 楷体
        # macOS
        'PingFang SC',         # 苹方-简 (most common on macOS)
        'STHeiti',             # 华文黑体
        'STSong',              # 华文宋体
        'Arial Unicode MS',    # Supports Chinese (if available)
        # Linux
        'Noto Sans CJK SC',    # Google Noto (common on Linux)
        'Source Han Sans SC',  # Adobe Source Han Sans
        'WenQuanYi Micro Hei', # 文泉驿微米黑
        'WenQuanYi Zen Hei',   # 文泉驿正黑
    ]
    
    available_chinese_fonts = []
    for font_name in chinese_font_candidates:
        if _check_font_available([font_name]):
            available_chinese_fonts.append(font_name)
            # Return up to 2 fonts for better fallback, but keep the list manageable
            if len(available_chinese_fonts) >= 2:
                break
    
    return available_chinese_fonts

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
    # Validate input
    if not isinstance(font_names, list) or len(font_names) == 0:
        return False
    
    # Normalize font names (strip whitespace, handle None)
    font_names = [str(f).strip() for f in font_names if f is not None]
    if len(font_names) == 0:
        return False
    
    # Use cache to avoid repeated checks
    cache_key = tuple(sorted(font_names))
    if cache_key in _font_availability_cache:
        return _font_availability_cache[cache_key]
    
    # Safely access font manager
    try:
        # Check if font manager is initialized
        if not hasattr(fm, 'fontManager') or fm.fontManager is None:
            logger.warning("Matplotlib font manager is not initialized.")
            return False
        
        # Get available fonts with error handling
        try:
            available_fonts = {f.name for f in fm.fontManager.ttflist}
        except (AttributeError, TypeError) as e:
            logger.warning(f"Failed to access font list: {e}")
            return False
        
        result = any(font_name in available_fonts for font_name in font_names)
        _font_availability_cache[cache_key] = result
        return result
    
    except Exception as e:
        logger.error(f"Unexpected error checking font availability: {e}")
        return False

def _register_bundled_fonts(font_family: str = 'all') -> None:
    """
    Scans the internal 'fonts' directory and registers Arimo/Tinos 
    with Matplotlib's font manager dynamically.
    Only registers fonts if they haven't been registered already.
    
    Parameters
    ----------
    font_family : str, optional
        Which font family to register: 'sans-serif' (Arimo only), 
        'serif' (Tinos only), or 'all' (both). Default is 'all'.
    """
    # Check if font directory exists
    if not FONT_DIR.exists():
        logger.error(f"Font directory not found: {FONT_DIR}")
        return
    
    # Check if font manager is available
    if not hasattr(fm, 'fontManager') or fm.fontManager is None:
        logger.error("Matplotlib font manager is not initialized.")
        return

    # Determine which fonts to register
    if font_family == 'sans-serif':
        font_prefixes = ['Arimo']
    elif font_family == 'serif':
        font_prefixes = ['Tinos']
    else:  # 'all' or default
        font_prefixes = ['Arimo', 'Tinos']

    registered_count = 0
    skipped_count = 0
    
    for font_path in FONT_DIR.glob("*.ttf"):
        # Only register fonts matching the requested family
        font_name = font_path.stem
        if not any(font_name.startswith(prefix) for prefix in font_prefixes):
            continue
        
        # Skip if already registered
        font_path_str = str(font_path)
        if font_path_str in _registered_bundled_fonts:
            skipped_count += 1
            continue
        
        # Validate file exists and is readable
        if not font_path.is_file():
            logger.warning(f"Font path is not a file: {font_path}")
            continue
        
        try:
            # Register font
            fm.fontManager.addfont(font_path_str)
            _registered_bundled_fonts.add(font_path_str)
            registered_count += 1
        except (OSError, IOError) as e:
            logger.warning(f"Failed to read font file {font_path.name}: {e}")
        except (ValueError, RuntimeError) as e:
            logger.warning(f"Failed to load font {font_path.name}: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error loading font {font_path.name}: {e}")

    # Clear cache after registering fonts so subsequent checks are accurate
    if registered_count > 0:
        _clear_font_cache()
        logger.debug(f"Registered {registered_count} bundled font(s).")
    if skipped_count > 0:
        logger.debug(f"Skipped {skipped_count} already registered font(s).")

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

def _configure_jupyter_retina() -> None:
    """
    Configure high-resolution display for Jupyter/IPython environments.
    Sets InlineBackend.figure_format to 'retina' if running in Jupyter notebook.
    This improves figure quality on high-resolution displays (e.g., Retina screens).
    """
    try:
        # Check if we're in IPython/Jupyter environment
        try:
            from IPython import get_ipython
            ipython = get_ipython()
        except ImportError:
            # IPython not available, skip
            return
        
        if ipython is None:
            # Not in IPython environment
            return
        
        # Check if we're in a Jupyter notebook (has kernel attribute)
        # This distinguishes notebooks from IPython shell
        if hasattr(ipython, 'kernel') and ipython.kernel is not None:
            # We're in a Jupyter notebook - enable retina display
            try:
                from IPython.display import set_matplotlib_formats
                set_matplotlib_formats('retina')
            except (ImportError, ValueError):
                # If set_matplotlib_formats is not available or retina is not supported,
                # silently skip - this is a nice-to-have feature
                pass
    except Exception:
        # Silently fail if anything goes wrong - this is a nice-to-have feature
        # We don't want to break scifont if IPython detection fails
        pass

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
        - 'zh': Chinese font style. Uses available Chinese fonts for both Chinese and English text.
    dpi : int
        Resolution for raster outputs (default: 300). Must be between 50 and 2000.
    
    Raises
    ------
    TypeError
        If style is not a string or dpi is not an integer.
    ValueError
        If style is empty or dpi is out of valid range.
    """
    # Validate and normalize style parameter
    if not isinstance(style, str):
        raise TypeError(f"style must be a string, got {type(style).__name__}")
    
    style = style.lower().strip()
    if not style:
        raise ValueError("style cannot be empty")
    
    # Validate dpi parameter
    if not isinstance(dpi, (int, float)):
        raise TypeError(f"dpi must be a number, got {type(dpi).__name__}")
    
    dpi = int(dpi)
    if dpi < 50 or dpi > 2000:
        raise ValueError(f"dpi must be between 50 and 2000, got {dpi}")
    
    # 1. Check system fonts and register bundled fonts only if needed
    system_fonts_available = False
    
    if style == 'zh':
        # Chinese style: use Chinese fonts directly
        # No need to check system fonts, we'll use Chinese fonts directly
        pass
    
    elif style in ['nature', 'cell', 'science']:
        # Sans-serif styles need Arial/Helvetica or Arimo
        system_fonts_available = _check_font_available(['Arial', 'Helvetica'])
        if not system_fonts_available:
            _register_bundled_fonts('sans-serif')  # Only register Arimo
            logger.info("System fonts (Arial/Helvetica) not found. Using bundled Arimo font.")
    
    elif style == 'ieee':
        # Serif styles need Times New Roman/Times or Tinos
        system_fonts_available = _check_font_available(['Times New Roman', 'Times'])
        if not system_fonts_available:
            _register_bundled_fonts('serif')  # Only register Tinos
            logger.info("System fonts (Times New Roman/Times) not found. Using bundled Tinos font.")
    
    else:
        # Unknown styles: register all fonts as fallback
        system_fonts_available = _check_font_available(['Arial', 'Helvetica'])
        if not system_fonts_available:
            _register_bundled_fonts('all')  # Register all fonts
    
    # 2. Ensure Editability
    try:
        _configure_vector_output()
    except Exception as e:
        logger.warning(f"Failed to configure vector output settings: {e}")
    
    # 2.5. Configure Jupyter/IPython retina display (if applicable)
    _configure_jupyter_retina()
    
    # 3. Base Configuration
    try:
        rcParams['figure.dpi'] = dpi
        rcParams['savefig.dpi'] = dpi
        rcParams['axes.unicode_minus'] = False  # Use hyphen instead of minus sign glyph
        
        # Scientific publication defaults
        # Disable grid by default (most journals prefer no grid)
        rcParams['axes.grid'] = False
        
        # Set tick direction inward for cleaner look
        rcParams['xtick.direction'] = 'in'
        rcParams['ytick.direction'] = 'in'
        
        # Set tick length (in points) - moderate length for clarity
        rcParams['xtick.major.size'] = 3.5
        rcParams['ytick.major.size'] = 3.5
        rcParams['xtick.minor.size'] = 2.0
        rcParams['ytick.minor.size'] = 2.0
        
        # Color cycle: matplotlib's default 'tab10' is colorblind-friendly
        # Users can override with plt.rcParams['axes.prop_cycle'] if needed
        
    except Exception as e:
        logger.error(f"Failed to set base configuration: {e}")
        raise

    # 4. Apply Journal-Specific Settings
    # Use the font availability result from step 1 (after potential registration)
    try:
        if style == 'zh':
            # Chinese style: use Chinese fonts directly
            chinese_fonts = _get_chinese_fonts()
            if not chinese_fonts:
                logger.warning("No Chinese fonts found on the system. Chinese text may not display correctly.")
                # Fallback to DejaVu Sans as last resort
                rcParams['font.family'] = 'sans-serif'
                rcParams['font.sans-serif'] = ['DejaVu Sans', 'sans-serif']
            else:
                # Use Chinese fonts as primary fonts
                # Most Chinese fonts also support English, so this works for both
                rcParams['font.family'] = 'sans-serif'
                rcParams['font.sans-serif'] = chinese_fonts + ['DejaVu Sans', 'sans-serif']
                logger.info(f"Applied 'Chinese' style ({chinese_fonts[0]}/Sans-serif, 8pt base).")
            
            # Use similar settings to 'cell' style for readability
            rcParams['font.size'] = 8
            rcParams['axes.labelsize'] = 9
            rcParams['xtick.labelsize'] = 8
            rcParams['ytick.labelsize'] = 8
            rcParams['legend.fontsize'] = 7
            # Line widths for Chinese style
            rcParams['axes.linewidth'] = 1.0  # Standard axes width
            rcParams['lines.linewidth'] = 1.0  # Standard data line width
            # Grid disabled by default
        
        elif style == 'nature':
            # Nature Guidelines: Sans-serif, 5-7pt.
            # Use the font availability determined in step 1
            rcParams['font.family'] = 'sans-serif'
            
            if system_fonts_available:
                rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'Arimo', 'DejaVu Sans']
                font_info = "Arial/Helvetica"
            else:
                # Re-check after registration to ensure Arimo is available
                if _check_font_available(['Arimo']):
                    rcParams['font.sans-serif'] = ['Arimo', 'DejaVu Sans']
                    font_info = "Arimo"
                else:
                    # Fallback to system defaults if Arimo registration failed
                    rcParams['font.sans-serif'] = ['DejaVu Sans', 'sans-serif']
                    font_info = "DejaVu Sans (fallback)"
                    logger.warning("Bundled Arimo font not available. Using system default.")
            
            rcParams['font.size'] = 7
            rcParams['axes.labelsize'] = 8  # Increased for better readability
            rcParams['xtick.labelsize'] = 7  # Increased, now matches base font size
            rcParams['ytick.labelsize'] = 7  # Increased, now matches base font size
            rcParams['legend.fontsize'] = 6
            # Line widths for Nature style (thin axes, standard data lines)
            rcParams['axes.linewidth'] = 0.5  # Thin axes for clean look
            rcParams['lines.linewidth'] = 1.0  # Standard data line width
            # Grid disabled by default (Nature typically doesn't use grid)
            
            # Only log when using fallback font, otherwise silent success
            if font_info == "Arimo":
                logger.info(f"Applied 'Nature' style ({font_info}/Sans-serif, 7pt base).")

        elif style == 'cell':
            # Cell Guidelines: Sans-serif, 6-8pt.
            rcParams['font.family'] = 'sans-serif'
            
            if system_fonts_available:
                rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'Arimo', 'DejaVu Sans']
                font_info = "Arial/Helvetica"
            else:
                if _check_font_available(['Arimo']):
                    rcParams['font.sans-serif'] = ['Arimo', 'DejaVu Sans']
                    font_info = "Arimo"
                else:
                    rcParams['font.sans-serif'] = ['DejaVu Sans', 'sans-serif']
                    font_info = "DejaVu Sans (fallback)"
                    logger.warning("Bundled Arimo font not available. Using system default.")
            
            rcParams['font.size'] = 8
            rcParams['axes.labelsize'] = 9  # Increased for better readability
            rcParams['xtick.labelsize'] = 8  # Increased, now matches base font size
            rcParams['ytick.labelsize'] = 8  # Increased, now matches base font size
            rcParams['legend.fontsize'] = 7
            # Line widths for Cell style
            rcParams['axes.linewidth'] = 1.0  # Standard axes width
            rcParams['lines.linewidth'] = 1.0  # Standard data line width
            # Grid disabled by default
            
            # Only log when using fallback font, otherwise silent success
            if font_info == "Arimo":
                logger.info(f"Applied 'Cell' style ({font_info}/Sans-serif, 8pt base).")

        elif style == 'science':
            # Science Guidelines: Sans-serif, similar to Nature but slightly larger.
            rcParams['font.family'] = 'sans-serif'
            
            if system_fonts_available:
                rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'Arimo', 'DejaVu Sans']
                font_info = "Arial/Helvetica"
            else:
                if _check_font_available(['Arimo']):
                    rcParams['font.sans-serif'] = ['Arimo', 'DejaVu Sans']
                    font_info = "Arimo"
                else:
                    rcParams['font.sans-serif'] = ['DejaVu Sans', 'sans-serif']
                    font_info = "DejaVu Sans (fallback)"
                    logger.warning("Bundled Arimo font not available. Using system default.")
            
            rcParams['font.size'] = 8
            rcParams['axes.labelsize'] = 10  # Increased for better readability
            rcParams['xtick.labelsize'] = 9  # Increased, maintains 1pt difference from axes labels
            rcParams['ytick.labelsize'] = 9  # Increased, maintains 1pt difference from axes labels
            rcParams['legend.fontsize'] = 8
            # Line widths for Science style
            rcParams['axes.linewidth'] = 1.0  # Standard axes width
            rcParams['lines.linewidth'] = 1.0  # Standard data line width
            # Grid disabled by default
            
            # Only log when using fallback font, otherwise silent success
            if font_info == "Arimo":
                logger.info(f"Applied 'Science' style ({font_info}/Sans-serif, 8-9pt base).")

        elif style == 'ieee':
            # IEEE Guidelines: Serif (Times), ~8pt.
            rcParams['font.family'] = 'serif'
            
            if system_fonts_available:
                rcParams['font.serif'] = ['Times New Roman', 'Times', 'Tinos', 'DejaVu Serif']
                font_info = "Times New Roman/Times"
            else:
                if _check_font_available(['Tinos']):
                    rcParams['font.serif'] = ['Tinos', 'DejaVu Serif']
                    font_info = "Tinos"
                else:
                    rcParams['font.serif'] = ['DejaVu Serif', 'serif']
                    font_info = "DejaVu Serif (fallback)"
                    logger.warning("Bundled Tinos font not available. Using system default.")
            
            rcParams['font.size'] = 8
            rcParams['axes.labelsize'] = 9  # Increased for better readability
            rcParams['xtick.labelsize'] = 9  # Increased, matches axes labels for consistency
            rcParams['ytick.labelsize'] = 9  # Increased, matches axes labels for consistency
            rcParams['legend.fontsize'] = 8
            # Line widths for IEEE style
            rcParams['axes.linewidth'] = 1.0  # Standard axes width
            rcParams['lines.linewidth'] = 1.0  # Standard data line width
            # IEEE figures often look better with subtle grid
            rcParams['axes.grid'] = True
            rcParams['grid.alpha'] = 0.3  # More subtle grid (reduced from 0.4)
            rcParams['grid.linewidth'] = 0.5  # Thin grid lines
            rcParams['grid.linestyle'] = '--'  # Dashed grid
            
            # Only log when using fallback font, otherwise silent success
            if font_info == "Tinos":
                logger.info(f"Applied 'IEEE' style ({font_info}/Serif, 8pt base).")

        else:
            # Default fallback for unknown styles
            rcParams['font.family'] = 'sans-serif'
            
            if system_fonts_available:
                rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'Arimo', 'sans-serif']
            else:
                if _check_font_available(['Arimo']):
                    rcParams['font.sans-serif'] = ['Arimo', 'sans-serif']
                else:
                    rcParams['font.sans-serif'] = ['sans-serif']
            
            logger.warning(f"Unknown style '{style}'. Loaded fonts but defaulted to basic settings.")
    
    except KeyError as e:
        logger.error(f"Failed to set Matplotlib parameter: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error applying style settings: {e}")
        raise

def get_style_info() -> dict:
    """
    Returns the current active font settings for debugging.
    
    Returns
    -------
    dict
        Dictionary containing current font configuration settings.
    """
    try:
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
    except Exception as e:
        logger.error(f"Failed to get style info: {e}")
        return {
            "font.family": "error",
            "pdf.fonttype": "error",
            "font.size": "error",
            "font.sans-serif": [],
            "font.serif": []
        }