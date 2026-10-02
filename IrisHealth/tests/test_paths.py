"""
Pruebas unitarias para la resolucion dinamica de rutas (app.constants.paths).
Verifica que las rutas se calculen relativamente sin cadenas de unidades fijas ni valores hardcodeados.
"""

import unittest
from pathlib import Path
from app.constants.paths import (
    PROJECT_ROOT,
    APP_DIR,
    ASSETS_DIR,
    LOGO_PATH,
    get_logo_path,
    get_samples_dir,
    get_default_reports_dir,
)


class TestPaths(unittest.TestCase):
    """Verifica resolucion de rutas dinamicas."""

    def test_project_root_exists(self):
        """Verifica que PROJECT_ROOT sea un directorio valido existente."""
        self.assertTrue(PROJECT_ROOT.is_dir())
        self.assertTrue((PROJECT_ROOT / "main.py").is_file())

    def test_logo_path_dynamic_resolution(self):
        """Verifica que el logo institucional exista y sea accesible dinamicamente."""
        resolved_logo = get_logo_path()
        self.assertIsInstance(resolved_logo, Path)
        self.assertTrue(resolved_logo.is_file(), f"El archivo de logotipo no se encuentra en {resolved_logo}")
        self.assertEqual(resolved_logo.name, "iris_logo.png")

    def test_samples_and_reports_dir_creation(self):
        """Verifica que los directorios de muestras y reportes se resuelvan y creen sin error."""
        samples_dir = get_samples_dir()
        self.assertTrue(samples_dir.is_dir())

        reports_dir = get_default_reports_dir()
        self.assertTrue(reports_dir.is_dir())


if __name__ == "__main__":
    unittest.main()
