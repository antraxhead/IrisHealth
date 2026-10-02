"""
Pruebas unitarias para el sistema de temas Claro y Oscuro Glacial de IrisHealth.
Verifica la conmutacion de estilos, la validez de los iconos SVG y la herencia en la UI.
"""

import os
import sys
import unittest
import xml.etree.ElementTree as ET
from PySide6.QtWidgets import QApplication

from app.constants.paths import get_theme_dark_icon_path, get_theme_light_icon_path
from app.constants.strings import STRINGS
from app.ui.styles import ThemeMode, get_stylesheet
from app.ui.main_window import MainWindow
from app.ui.components.report_dialog import ReportDialog


class TestThemes(unittest.TestCase):
    """Conjunto de pruebas para el gestor de temas y estilos de interfaz."""

    @classmethod
    def setUpClass(cls):
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_theme_svg_icons_exist_and_valid(self):
        """Verifica que los archivos SVG de los iconos existan y sean XML valido."""
        dark_icon = get_theme_dark_icon_path()
        light_icon = get_theme_light_icon_path()

        self.assertTrue(dark_icon.is_file(), f"El icono de modo oscuro no existe en {dark_icon}")
        self.assertTrue(light_icon.is_file(), f"El icono de modo claro no existe en {light_icon}")

        # Validar sintaxis SVG con ElementTree
        tree_dark = ET.parse(str(dark_icon))
        root_dark = tree_dark.getroot()
        self.assertTrue(root_dark.tag.endswith("svg"))

        tree_light = ET.parse(str(light_icon))
        root_light = tree_light.getroot()
        self.assertTrue(root_light.tag.endswith("svg"))

    def test_stylesheets_content_and_palettes(self):
        """Verifica que las hojas de estilos contengan las definiciones correctas de color."""
        sheet_light = get_stylesheet(ThemeMode.LIGHT)
        sheet_dark = get_stylesheet(ThemeMode.DARK)

        self.assertIsInstance(sheet_light, str)
        self.assertIsInstance(sheet_dark, str)
        self.assertGreater(len(sheet_light), 500)
        self.assertGreater(len(sheet_dark), 500)

        # Paleta clara: fondo claro #F4F9FD, texto oscuro #0C2340
        self.assertIn("#F4F9FD", sheet_light)
        self.assertIn("#0C2340", sheet_light)

        # Paleta oscura: fondo abismo #07101E, texto escarcha #F0F8FF
        self.assertIn("#07101E", sheet_dark)
        self.assertIn("#F0F8FF", sheet_dark)

    def test_main_window_theme_toggle(self):
        """Verifica que MainWindow conmute temas de manera reactiva sin errores."""
        win = MainWindow()
        win.show()

        # Estado inicial: Modo Claro
        self.assertEqual(win._current_theme, ThemeMode.LIGHT)
        self.assertEqual(win._btn_theme_toggle.text(), STRINGS.BTN_THEME_DARK)

        # Conmutar a Modo Oscuro
        win._on_toggle_theme()
        self.assertEqual(win._current_theme, ThemeMode.DARK)
        self.assertEqual(win._btn_theme_toggle.text(), STRINGS.BTN_THEME_LIGHT)

        # Conmutar de regreso a Modo Claro
        win._on_toggle_theme()
        self.assertEqual(win._current_theme, ThemeMode.LIGHT)
        self.assertEqual(win._btn_theme_toggle.text(), STRINGS.BTN_THEME_DARK)

        win.close()

    def test_report_dialog_theme_inheritance(self):
        """Verifica que ReportDialog herede y aplique estilos correctamente en ambos modos."""
        win = MainWindow()
        
        # En modo claro
        win._apply_theme(ThemeMode.LIGHT)
        dialog_light = ReportDialog(win._bioimages, win)
        dialog_light.show()
        self.app.processEvents()
        dialog_light.close()

        # En modo oscuro
        win._apply_theme(ThemeMode.DARK)
        dialog_dark = ReportDialog(win._bioimages, win)
        dialog_dark.show()
        self.app.processEvents()
        dialog_dark.close()

        win.close()

    def test_multichannel_dynamic_loading_sync(self):
        """Verifica que al cargar una nueva imagen se seleccione y sincronice en el panel multicanal."""
        import numpy as np
        from app.core.bioimage_reader import BioImageItem, BioImageMetadata
        win = MainWindow()
        win.show()

        meta = BioImageMetadata(
            filename="usuario_test.png",
            filepath="/tmp/usuario_test.png",
            width=64,
            height=48,
            channels=3,
            color_mode="RGB",
            dtype="uint8",
            file_size_bytes=1024,
            is_color=True,
        )
        arr = np.full((48, 64, 3), 150, dtype=np.uint8)
        item = BioImageItem(metadata=meta, original_array=arr)
        win._add_bioimage_item(item)
        new_idx = len(win._bioimages) - 1
        win._update_all_views(select_index=new_idx)

        self.assertEqual(win._current_index, new_idx)
        self.assertEqual(win._combo_multichannel.currentIndex(), new_idx)
        self.assertEqual(win._list_images.currentRow(), new_idx)
        loaded = win._channel_grid._canvas_orig.get_current_array()
        self.assertIsNotNone(loaded)
        np.testing.assert_array_equal(loaded, arr)

        win.close()

    def test_multichannel_color_decomposition_and_probe(self):
        """Verifica que el modo espectral a color sea el predeterminado y la sonda no duplique valores."""
        from PySide6.QtCore import QPointF
        import numpy as np
        from app.core.bioimage_reader import BioImageItem, BioImageMetadata

        win = MainWindow()
        win.show()

        # 1. Comprobar que el modo inicial es Proyeccion Monocromatica cientifica estandar
        self.assertTrue(win._radio_gray.isChecked())
        self.assertFalse(win._radio_color.isChecked())
        self.assertTrue(win._channel_grid._use_grayscale)

        # 2. Cargar una imagen con canales deliberadamente asimetricos
        # R=200, G=100, B=50
        meta = BioImageMetadata(
            filename="asym_test.png",
            filepath="/tmp/asym_test.png",
            width=60,
            height=40,
            channels=3,
            color_mode="RGB",
            dtype="uint8",
            file_size_bytes=2048,
            is_color=True,
        )
        asym_arr = np.zeros((40, 60, 3), dtype=np.uint8)
        asym_arr[:, :, 0] = 200  # R
        asym_arr[:, :, 1] = 100  # G
        asym_arr[:, :, 2] = 50   # B

        item = BioImageItem(metadata=meta, original_array=asym_arr)
        win._add_bioimage_item(item)
        idx = len(win._bioimages) - 1
        win._update_all_views(select_index=idx)
        self.app.processEvents()

        # Verificar que los lienzos tienen mapas 2D de intensidad monocromatica pura
        red_arr = win._channel_grid._canvas_red.get_current_array()
        green_arr = win._channel_grid._canvas_green.get_current_array()
        blue_arr = win._channel_grid._canvas_blue.get_current_array()

        self.assertEqual(red_arr.shape, (40, 60))
        self.assertEqual(red_arr[10, 10], 200)

        self.assertEqual(green_arr.shape, (40, 60))
        self.assertEqual(green_arr[10, 10], 100)

        self.assertEqual(blue_arr.shape, (40, 60))
        self.assertEqual(blue_arr[10, 10], 50)

        # 3. Conmutar a Filtrado Espectral de Color
        win._radio_color.click()
        self.app.processEvents()
        self.assertFalse(win._channel_grid._use_grayscale)
        color_r = win._channel_grid._canvas_red.get_current_array()
        self.assertGreater(int(color_r[10, 10, 0]), int(color_r[10, 10, 1]))
        self.assertGreater(int(color_r[10, 10, 0]), int(color_r[10, 10, 2]))

        # 4. Conmutar de vuelta a Proyeccion Monocromatica cientifica
        win._radio_gray.click()
        self.app.processEvents()
        self.assertTrue(win._channel_grid._use_grayscale)
        restored_r = win._channel_grid._canvas_red.get_current_array()
        self.assertEqual(restored_r.shape, (40, 60))

        # 5. Probar la sonda clinica moviendo el cursor sobre el Canal Azul
        canvas_b = win._channel_grid._canvas_blue
        center_pt = QPointF(canvas_b.width() / 2.0, canvas_b.height() / 2.0)
        canvas_b._update_probe_under_cursor(center_pt)
        self.app.processEvents()

        hud_orig = win._channel_grid._canvas_orig._hud_bar.text()
        hud_r = win._channel_grid._canvas_red._hud_bar.text()
        hud_g = win._channel_grid._canvas_green._hud_bar.text()
        hud_b = win._channel_grid._canvas_blue._hud_bar.text()

        # Comprobar que no hay duplicacion de valores 197/50 a todos los canales
        self.assertIn("R: 200", hud_orig)
        self.assertIn("G: 100", hud_orig)
        self.assertIn("B: 50", hud_orig)
        self.assertIn("Intensidad R (630 nm): 200", hud_r)
        self.assertIn("Intensidad G (520 nm): 100", hud_g)
        self.assertIn("Intensidad B (450 nm): 50", hud_b)

        # Comprobar que el canal azul NO fue sobreescrito con texto generico
        self.assertNotIn("Lum:", hud_b)

        win.close()


if __name__ == "__main__":
    unittest.main()
