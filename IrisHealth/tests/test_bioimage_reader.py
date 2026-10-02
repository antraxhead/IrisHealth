"""
Pruebas unitarias para el lector y validador de bioimagenes (BioImageReader).
"""

import os
import tempfile
import unittest
from pathlib import Path
import numpy as np
from PIL import Image

from app.core.bioimage_reader import BioImageReader, BioImageItem, BioImageLoadError
from app.samples.sample_generator import SampleBioImageGenerator


class TestBioImageReader(unittest.TestCase):
    """Conjunto de pruebas para BioImageReader."""

    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp(prefix="bioimage_test_")
        cls.sample_paths = SampleBioImageGenerator.ensure_sample_images_exist(cls.test_dir)

    @classmethod
    def tearDownClass(cls):
        for p in Path(cls.test_dir).glob("*"):
            try:
                os.remove(p)
            except Exception:
                pass
        try:
            os.rmdir(cls.test_dir)
        except Exception:
            pass

    def test_load_valid_sample_images(self):
        """Verifica que las bioimagenes de muestra se carguen correctamente."""
        for path in self.sample_paths:
            item = BioImageReader.load_from_file(path)
            self.assertIsInstance(item, BioImageItem)
            self.assertEqual(item.metadata.filename, path.name)
            self.assertEqual(item.metadata.channels, 3)
            self.assertTrue(item.metadata.is_color)
            self.assertGreater(item.metadata.width, 0)
            self.assertGreater(item.metadata.height, 0)
            self.assertEqual(item.original_array.shape, (item.metadata.height, item.metadata.width, 3))

    def test_nonexistent_file_raises_error(self):
        """Verifica que un archivo inexistente lance BioImageLoadError."""
        fake_path = Path(self.test_dir) / "archivo_fantasma.png"
        with self.assertRaises(BioImageLoadError):
            BioImageReader.load_from_file(fake_path)

    def test_unsupported_extension_raises_error(self):
        """Verifica que una extension no soportada lance BioImageLoadError."""
        txt_path = Path(self.test_dir) / "documento.txt"
        txt_path.write_text("contenido invalido")
        with self.assertRaises(BioImageLoadError):
            BioImageReader.load_from_file(txt_path)

    def test_load_grayscale_bioimage(self):
        """Verifica la deteccion correcta de una imagen en escala de grises."""
        gray_arr = np.zeros((100, 100), dtype=np.uint8)
        gray_path = Path(self.test_dir) / "grayscale_bioimage.png"
        Image.fromarray(gray_arr, mode="L").save(gray_path)

        item = BioImageReader.load_from_file(gray_path)
        self.assertFalse(item.metadata.is_color)
        self.assertEqual(item.metadata.color_mode, "L")


if __name__ == "__main__":
    unittest.main()
