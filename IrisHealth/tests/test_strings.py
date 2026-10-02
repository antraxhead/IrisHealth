"""
Pruebas unitarias para el archivo de strings y constantes del sistema.
Verifica que no existan valores vacios ni emojis en ninguna cadena.
"""

import re
import unittest
from app.constants.strings import STRINGS, AppStrings


class TestStrings(unittest.TestCase):
    """Verifica integridad y ausencia de emojis en las constantes de texto."""

    EMOJI_PATTERN = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticones
        "\U0001F300-\U0001F5FF"  # Simbolos y pictogramas diversos
        "\U0001F680-\U0001F6FF"  # Transporte y mapas
        "\U0001F700-\U0001F77F"  # Simbolos alquimicos
        "\U0001F780-\U0001F7FF"  # Geometricos extendidos
        "\U0001F800-\U0001F8FF"  # Flechas suplementarias
        "\U0001F900-\U0001F9FF"  # Simbolos suplementarios
        "\U0001FA00-\U0001FA6F"  # Ajedrez / simbolos extendidos
        "\U0001FA70-\U0001FAFF"  # Simbolos diversos
        "\u2600-\u26FF"          # Simbolos varios
        "\u2700-\u27BF"          # Dingbats
        "]+",
        flags=re.UNICODE
    )

    def test_no_empty_strings(self):
        """Verifica que ninguna constante de texto este vacia."""
        for field_name in AppStrings.__dataclass_fields__:
            val = getattr(STRINGS, field_name)
            self.assertIsInstance(val, str, f"El campo {field_name} debe ser una cadena de texto.")
            self.assertTrue(len(val.strip()) > 0, f"El campo {field_name} no debe estar vacio.")

    def test_strict_no_emojis(self):
        """Verifica que ninguna cadena de la aplicacion contenga emojis."""
        for field_name in AppStrings.__dataclass_fields__:
            val = getattr(STRINGS, field_name)
            matches = self.EMOJI_PATTERN.findall(val)
            self.assertEqual(
                len(matches),
                0,
                f"El campo '{field_name}' contiene emojis no permitidos: {matches}"
            )

    def test_formatting_strings_syntax(self):
        """Verifica que las cadenas con parametros de formato sean validas."""
        test_cases = [
            (STRINGS.EXPLORER_COUNT_LABEL, {"count": 3}),
            (STRINGS.EXPLORER_SERIES_INSUFFICIENT, {"count": 2}),
            (STRINGS.META_FILENAME, {"filename": "test.png"}),
            (STRINGS.META_FILEPATH, {"filepath": "/path/to/test.png"}),
            (STRINGS.META_DIMENSIONS, {"width": 800, "height": 600}),
            (STRINGS.META_CHANNELS, {"channels": 3, "color_mode": "RGB"}),
            (STRINGS.META_DTYPE, {"dtype": "uint8"}),
            (STRINGS.META_SIZE_BYTES, {"size_kb": 128.5}),
            (STRINGS.MULTICHANNEL_STATS_FORMAT, {"channel": "Rojo", "mean": 120.5, "min": 0, "max": 255, "std": 32.1}),
            (STRINGS.MULTICHANNEL_STATS_SHORT_FORMAT, {"mean": 120.5, "min": 0, "max": 255, "std": 32.1}),
            (STRINGS.MULTICHANNEL_PROBE_BAND_FORMAT, {"x": 10, "y": 20, "band": "R", "val": 150}),
            (STRINGS.FILTER_LABEL_BRIGHTNESS, {"val": 15}),
            (STRINGS.FILTER_LABEL_CONTRAST, {"val": 1.25}),
            (STRINGS.FILTER_LABEL_GAMMA, {"val": 0.95}),
            (STRINGS.FILTER_LABEL_PHASE_RED, {"val": 1.1}),
            (STRINGS.FILTER_LABEL_PHASE_GREEN, {"val": 1.0}),
            (STRINGS.FILTER_LABEL_PHASE_BLUE, {"val": 0.8}),
            (STRINGS.HUD_PROBE_TEXT, {"x": 100, "y": 200, "r": 255, "g": 128, "b": 64, "lum": 150}),
            (STRINGS.HUD_MEASURE_TEXT, {"pixels": 142.5, "microns": 64.1}),
            (STRINGS.ERR_LESS_THAN_THREE_IMAGES, {"count": 2}),
            (STRINGS.ERR_IMAGE_NOT_COLOR, {"name": "gris.png"}),
            (STRINGS.ERR_LOAD_FAILED, {"filepath": "a.png", "reason": "test"}),
            (STRINGS.ERR_PROCESS_FAILED, {"reason": "test"}),
            (STRINGS.ERR_PDF_GENERATION_FAILED, {"reason": "test"}),
            (STRINGS.PDF_AUTHOR_LABEL, {"lastname": "Perez", "firstname": "Juan"}),
            (STRINGS.PDF_DATE_LABEL, {"date": "2026-09-12"}),
            (STRINGS.MSG_IMAGE_EXPORTED, {"filepath": "out.png"}),
        ]
        for template, kwargs in test_cases:
            formatted = template.format(**kwargs)
            self.assertIsInstance(formatted, str)
            self.assertTrue(len(formatted) > 0)


if __name__ == "__main__":
    unittest.main()
