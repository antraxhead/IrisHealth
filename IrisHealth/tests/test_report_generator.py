"""
Pruebas unitarias para la generacion automatica de reportes PDF academicos.
"""

import os
import tempfile
import unittest
from pathlib import Path

from app.core.bioimage_reader import BioImageReader
from app.core.report_generator import ReportGenerator, ReportGeneratorError
from app.samples.sample_generator import SampleBioImageGenerator


class TestReportGenerator(unittest.TestCase):
    """Conjunto de pruebas para ReportGenerator."""

    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp(prefix="report_test_")
        cls.output_dir = tempfile.mkdtemp(prefix="report_out_")
        cls.sample_paths = SampleBioImageGenerator.ensure_sample_images_exist(cls.test_dir)
        cls.bioimages = [BioImageReader.load_from_file(p) for p in cls.sample_paths]

    @classmethod
    def tearDownClass(cls):
        for d in [cls.test_dir, cls.output_dir]:
            for p in Path(d).glob("*"):
                try:
                    os.remove(p)
                except Exception:
                    pass
            try:
                os.rmdir(d)
            except Exception:
                pass

    def test_standard_filename_generation(self):
        """Verifica que el formato del nombre cumpla con la especificacion exacta."""
        fname_21 = ReportGenerator.build_standard_filename("Mendizabal", "Eduardo", "Actividad2.1")
        self.assertEqual(fname_21, "Mendizabal_Eduardo_Actividad2.1.pdf")

        fname_22 = ReportGenerator.build_standard_filename("Mendizabal Ruiz", "Eduardo", "Actividad2.2")
        self.assertEqual(fname_22, "MendizabalRuiz_Eduardo_Actividad2.2.pdf")

    def test_generate_activity_2_1_pdf(self):
        """Verifica la generacion correcta del PDF de la Actividad 2.1."""
        pdf_path = ReportGenerator.generate_activity_2_1_pdf(
            lastname="Mendizabal",
            firstname="Eduardo",
            bioimages=self.bioimages,
            output_dir=self.output_dir,
        )
        self.assertTrue(pdf_path.exists())
        self.assertGreater(pdf_path.stat().st_size, 1000)
        self.assertEqual(pdf_path.name, "Mendizabal_Eduardo_Actividad2.1.pdf")

    def test_generate_activity_2_2_pdf(self):
        """Verifica la generacion correcta del PDF de la Actividad 2.2."""
        pdf_path = ReportGenerator.generate_activity_2_2_pdf(
            lastname="Mendizabal",
            firstname="Eduardo",
            bioimages=self.bioimages,
            output_dir=self.output_dir,
        )
        self.assertTrue(pdf_path.exists())
        self.assertGreater(pdf_path.stat().st_size, 1000)
        self.assertEqual(pdf_path.name, "Mendizabal_Eduardo_Actividad2.2.pdf")

    def test_insufficient_images_raises_error(self):
        """Verifica que intentar generar reporte con menos de 3 bioimagenes lance excepcion."""
        with self.assertRaises(ReportGeneratorError):
            ReportGenerator.generate_activity_2_1_pdf(
                lastname="Perez",
                firstname="Juan",
                bioimages=self.bioimages[:2],
                output_dir=self.output_dir,
            )

    def test_missing_student_names_raises_error(self):
        """Verifica que nombres vacios lancen excepcion."""
        with self.assertRaises(ReportGeneratorError):
            ReportGenerator.generate_activity_2_1_pdf(
                lastname="",
                firstname="Juan",
                bioimages=self.bioimages,
                output_dir=self.output_dir,
            )


if __name__ == "__main__":
    unittest.main()
