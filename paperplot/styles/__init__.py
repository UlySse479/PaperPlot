"""Built-in visual styles."""

from paperplot.styles.academic_bright import STYLE as ACADEMIC_BRIGHT_STYLE
from paperplot.styles.academic_muted import STYLE as ACADEMIC_MUTED_STYLE
from paperplot.styles.default import STYLE as DEFAULT_STYLE
from paperplot.styles.grayscale_safe import STYLE as GRAYSCALE_SAFE_STYLE
from paperplot.styles.nature_clean import STYLE as NATURE_CLEAN_STYLE


STYLES = {
    "default": DEFAULT_STYLE,
    "academic-muted": ACADEMIC_MUTED_STYLE,
    "academic-bright": ACADEMIC_BRIGHT_STYLE,
    "grayscale-safe": GRAYSCALE_SAFE_STYLE,
    "nature-clean": NATURE_CLEAN_STYLE,
}

__all__ = ["STYLES"]
