"""
Modulo de rutas dinamicas para IrisHealth.
Calcula todas las rutas relativas al proyecto para evitar rutas hardcodeadas.
Totalmente compatible con cualquier sistema operativo o directorio de instalacion.
"""

from pathlib import Path

# Directorio raiz de la aplicacion (app/)
APP_DIR = Path(__file__).resolve().parent.parent

# Directorio raiz del proyecto (IrisHealth/)
PROJECT_ROOT = APP_DIR.parent

# Directorio de recursos graficos y activos
ASSETS_DIR = APP_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "iris_logo.png"
THEME_DARK_ICON_PATH = ASSETS_DIR / "theme_dark.svg"
THEME_LIGHT_ICON_PATH = ASSETS_DIR / "theme_light.svg"

# Directorio de bioimagenes de muestra calibradas
SAMPLE_BIOIMAGES_DIR = PROJECT_ROOT / "assets" / "bioimages"

# Directorio predeterminado de reportes generados
DEFAULT_REPORTS_DIR = PROJECT_ROOT / "reportes"


def get_logo_path() -> Path:
    """Devuelve la ruta absoluta al logotipo institucional."""
    return LOGO_PATH


def get_theme_dark_icon_path() -> Path:
    """Devuelve la ruta al icono SVG de modo oscuro."""
    return THEME_DARK_ICON_PATH


def get_theme_light_icon_path() -> Path:
    """Devuelve la ruta al icono SVG de modo claro."""
    return THEME_LIGHT_ICON_PATH


def get_samples_dir() -> Path:
    """Devuelve la ruta al directorio de bioimagenes de muestra."""
    SAMPLE_BIOIMAGES_DIR.mkdir(parents=True, exist_ok=True)
    return SAMPLE_BIOIMAGES_DIR


def get_default_reports_dir() -> Path:
    """Devuelve la ruta al directorio predeterminado de reportes."""
    DEFAULT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_REPORTS_DIR
