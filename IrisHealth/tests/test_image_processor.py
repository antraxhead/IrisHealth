"""
Pruebas unitarias para el motor de procesamiento, filtrado y descomposicion multicanal (ImageProcessor).
"""

import unittest
import numpy as np
from PySide6.QtGui import QImage

from app.core.image_processor import (
    ImageProcessor,
    RGBDecompositionResult,
    ImageProcessingError,
)


class TestImageProcessor(unittest.TestCase):
    """Conjunto de pruebas para el motor ImageProcessor."""

    def setUp(self):
        self.height, self.width = 50, 60
        self.synthetic_rgb = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.synthetic_rgb[:, :, 0] = 180  # R
        self.synthetic_rgb[:, :, 1] = 90   # G
        self.synthetic_rgb[:, :, 2] = 45   # B

    def test_rgb_decomposition_shapes_and_values(self):
        """Verifica que la separacion de canales coincida exactamente con las matrices RGB."""
        decomp = ImageProcessor.decompose_rgb(self.synthetic_rgb)
        self.assertIsInstance(decomp, RGBDecompositionResult)

        self.assertEqual(decomp.original_rgb.shape, (self.height, self.width, 3))
        self.assertEqual(decomp.red_gray.shape, (self.height, self.width))
        self.assertEqual(decomp.green_gray.shape, (self.height, self.width))
        self.assertEqual(decomp.blue_gray.shape, (self.height, self.width))

        np.testing.assert_array_equal(decomp.red_gray, self.synthetic_rgb[:, :, 0])
        np.testing.assert_array_equal(decomp.green_gray, self.synthetic_rgb[:, :, 1])
        np.testing.assert_array_equal(decomp.blue_gray, self.synthetic_rgb[:, :, 2])

    def test_channel_statistics_calculation(self):
        """Verifica calculo cuantitativo de estadisticas por canal."""
        decomp = ImageProcessor.decompose_rgb(self.synthetic_rgb)

        self.assertEqual(decomp.stats_red.mean, 180.0)
        self.assertEqual(decomp.stats_red.min, 180.0)
        self.assertEqual(decomp.stats_red.max, 180.0)
        self.assertEqual(decomp.stats_red.std, 0.0)

    def test_apply_pipeline_luminance_and_phases(self):
        """Verifica ajustes de brillo, contraste, gamma y fases de color."""
        # Brillo positivo
        bright_img = ImageProcessor.apply_pipeline(self.synthetic_rgb, brightness=20)
        self.assertEqual(bright_img.shape, self.synthetic_rgb.shape)
        self.assertGreater(float(np.mean(bright_img)), float(np.mean(self.synthetic_rgb)))

        # Fases de color: Reducir fase roja a cero
        no_red = ImageProcessor.apply_pipeline(self.synthetic_rgb, phase_red=0.0)
        self.assertEqual(int(np.max(no_red[:, :, 0])), 0)
        self.assertEqual(int(np.mean(no_red[:, :, 1])), 90)

    def test_apply_pipeline_spatial_filters(self):
        """Verifica aplicacion de filtros de enfoque, desenfoque, sobel e inversion."""
        # Inversion
        inverted = ImageProcessor.apply_pipeline(self.synthetic_rgb, spatial_filter="invert")
        self.assertEqual(int(inverted[0, 0, 0]), 255 - 180)

        # Enfoque y Desenfoque
        sharpened = ImageProcessor.apply_pipeline(self.synthetic_rgb, spatial_filter="sharpen")
        blurred = ImageProcessor.apply_pipeline(self.synthetic_rgb, spatial_filter="blur")
        self.assertEqual(sharpened.shape, self.synthetic_rgb.shape)
        self.assertEqual(blurred.shape, self.synthetic_rgb.shape)

        # Sobel
        sobel = ImageProcessor.apply_pipeline(self.synthetic_rgb, spatial_filter="sobel")
        self.assertEqual(sobel.shape, self.synthetic_rgb.shape)

    def test_apply_pipeline_pseudocolor_lut(self):
        """Verifica aplicacion de tablas de color falso."""
        for lut in ("grayscale", "fluorescence", "thermal"):
            colored = ImageProcessor.apply_pipeline(self.synthetic_rgb, lut_mode=lut)
            self.assertEqual(colored.shape, (self.height, self.width, 3))
            self.assertEqual(colored.dtype, np.uint8)

    def test_calculate_histogram(self):
        """Verifica computo de histogramas multicanal."""
        hist = ImageProcessor.calculate_histogram(self.synthetic_rgb)
        self.assertIn("r", hist)
        self.assertIn("g", hist)
        self.assertIn("b", hist)
        self.assertIn("lum", hist)

        self.assertEqual(len(hist["r"]), 256)
        # La suma de frecuencias debe ser igual al total de pixeles
        total_pixels = self.height * self.width
        self.assertEqual(int(np.sum(hist["r"])), total_pixels)
        self.assertEqual(int(np.sum(hist["g"])), total_pixels)
        self.assertEqual(int(np.sum(hist["b"])), total_pixels)

    def test_numpy_to_qimage_conversion(self):
        """Verifica la conversion fluida a PySide6 QImage sin copias corruptas."""
        gray_arr = np.zeros((30, 40), dtype=np.uint8)
        qimg_gray = ImageProcessor.numpy_to_qimage(gray_arr)
        self.assertFalse(qimg_gray.isNull())
        self.assertEqual(qimg_gray.format(), QImage.Format.Format_Grayscale8)

        qimg_rgb = ImageProcessor.numpy_to_qimage(self.synthetic_rgb)
        self.assertFalse(qimg_rgb.isNull())
        self.assertEqual(qimg_rgb.format(), QImage.Format.Format_RGB888)


if __name__ == "__main__":
    unittest.main()
