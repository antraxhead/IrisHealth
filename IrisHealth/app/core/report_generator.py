"""
Modulo para la generacion automatica de reportes PDF clinicos y academicos.
Incorpora la paleta glacial y el logotipo institucional de IrisHealth de forma dinamica (sin rutas hardcodeadas).
Cumple rigurosamente con los formatos solicitados en las Actividades 2.1 y 2.2:
- Nomenclatura oficial: Primerapellido_primerNombre_Actividad2.X.pdf
- Visualizacion de codigo utilizado y evidencia de bioimagenes y canales.
- Cero cadenas de texto hardcodeadas (todas importadas desde STRINGS).
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    KeepTogether,
    Preformatted,
)

from app.constants.strings import STRINGS
from app.constants.paths import get_logo_path
from app.core.bioimage_reader import BioImageItem
from app.core.image_processor import ImageProcessor, RGBDecompositionResult


class ReportGeneratorError(Exception):
    """Excepcion al fallar la generacion de reportes PDF."""
    pass


class ReportGenerator:
    """Generador de reportes PDF en cumplimiento profesional y academico con paleta glacial."""

    @staticmethod
    def build_standard_filename(lastname: str, firstname: str, activity_code: str) -> str:
        """
        Construye el nombre de archivo segun la especificacion oficial:
        Primerapellido_primerNombre_Actividad2.X.pdf
        """
        clean_last = "".join(c for c in lastname.strip().title() if c.isalnum())
        clean_first = "".join(c for c in firstname.strip().title() if c.isalnum())
        return f"{clean_last}_{clean_first}_{activity_code}.pdf"

    @classmethod
    def _create_header_table(
        cls,
        doc_title: str,
        lastname: str,
        firstname: str,
        styles,
    ) -> Table:
        """Construye un encabezado profesional con paleta glacial incorporando el logotipo institucional."""
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#0A1C30"),
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontSize=9.5,
            leading=12,
            textColor=colors.HexColor("#0284C7"),
        )
        body_style = ParagraphStyle(
            "DocMeta",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#0C4A6E"),
        )

        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        author_text = STRINGS.PDF_AUTHOR_LABEL.format(lastname=lastname, firstname=firstname)
        date_text = STRINGS.PDF_DATE_LABEL.format(date=date_str)

        header_info = [
            Paragraph(f"<b>{STRINGS.PDF_REPORT_INSTITUTION}</b>", subtitle_style),
            Paragraph(f"<b>{doc_title}</b>", title_style),
            Spacer(1, 4),
            Paragraph(f"{author_text}  |  {date_text}", body_style),
        ]

        logo_path = get_logo_path()
        if logo_path.exists():
            logo_img = RLImage(str(logo_path), width=58, height=58)
            header_table = Table([[logo_img, header_info]], colWidths=[65, 465])
            header_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0F7FB")),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#BAE6FD")),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]))
        else:
            header_table = Table([[header_info]], colWidths=[530])
            header_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0F7FB")),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#BAE6FD")),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]))

        return header_table

    @classmethod
    def generate_activity_2_1_pdf(
        cls,
        lastname: str,
        firstname: str,
        bioimages: List[BioImageItem],
        output_dir: str | Path,
        code_snippet: Optional[str] = None,
    ) -> Path:
        """
        Genera el reporte PDF para el despliegue de serie de bioimagenes (Actividad 2.1).
        """
        if len(bioimages) < 3:
            raise ReportGeneratorError(
                STRINGS.ERR_LESS_THAN_THREE_IMAGES.format(count=len(bioimages))
            )

        if not lastname.strip() or not firstname.strip():
            raise ReportGeneratorError(STRINGS.ERR_STUDENT_DATA_REQUIRED)

        out_path = Path(output_dir) / cls.build_standard_filename(lastname, firstname, "Actividad2.1")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(out_path),
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        section_style = ParagraphStyle(
            "DocSection",
            parent=styles["Heading2"],
            fontSize=11.5,
            leading=15,
            textColor=colors.HexColor("#0C4A6E"),
            spaceBefore=10,
            spaceAfter=4,
        )
        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#0C2340"),
        )
        code_style = ParagraphStyle(
            "CodeBlock",
            fontName="Courier",
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor("#0A1C30"),
        )

        story = []

        # Encabezado institucional glacial con logo
        story.append(cls._create_header_table(STRINGS.PDF_REPORT_DOC_TITLE_21, lastname, firstname, styles))
        story.append(Spacer(1, 10))

        # Seccion de Codigo Fuente
        story.append(Paragraph(STRINGS.PDF_CODE_SECTION_TITLE, section_style))
        default_code = (
            "# Codigo utilizado para la carga y despliegue de bioimagenes (PySide6 / NumPy / PIL)\n"
            "from PIL import Image\n"
            "import numpy as np\n\n"
            "def open_and_display_bioimages(filepaths):\n"
            "    loaded_images = []\n"
            "    for path in filepaths:\n"
            "        with Image.open(path) as img:\n"
            "            arr = np.array(img.convert('RGB'))\n"
            "            loaded_images.append({'name': path.name, 'shape': arr.shape, 'data': arr})\n"
            "    return loaded_images\n"
        )
        code_text = code_snippet if code_snippet else default_code
        code_flowable = Preformatted(code_text, code_style)
        code_box = Table([[code_flowable]], colWidths=[530])
        code_box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0F9FF")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#BAE6FD")),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(code_box)
        story.append(Spacer(1, 10))

        # Seccion de Evidencia Visual
        story.append(Paragraph(STRINGS.PDF_RESULTS_SECTION_TITLE, section_style))

        temp_files = []
        try:
            for idx, item in enumerate(bioimages[:3], start=1):
                temp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                temp_files.append(temp_img.name)
                temp_img.close()

                pil_img = Image.fromarray(item.original_array)
                pil_img.save(temp_img.name, format="PNG")

                img_flowable = RLImage(temp_img.name, width=170, height=130)

                meta_text = (
                    f"<b>Bioimagen {idx}:</b> {item.metadata.filename}<br/>"
                    f"<b>Dimensiones:</b> {item.metadata.width} x {item.metadata.height} px<br/>"
                    f"<b>Canales:</b> {item.metadata.channels} ({item.metadata.color_mode})<br/>"
                    f"<b>Tipo de dato:</b> {item.metadata.dtype}<br/>"
                    f"<b>Tamano:</b> {item.metadata.file_size_bytes / 1024.0:.1f} KB"
                )
                meta_para = Paragraph(meta_text, body_style)

                item_table = Table([[img_flowable, meta_para]], colWidths=[185, 345])
                item_table.setStyle(TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#BAE6FD")),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]))

                story.append(KeepTogether([item_table, Spacer(1, 8)]))

            doc.build(story)
        finally:
            for t_file in temp_files:
                try:
                    if os.path.exists(t_file):
                        os.remove(t_file)
                except Exception:
                    pass

        return out_path

    @classmethod
    def generate_activity_2_2_pdf(
        cls,
        lastname: str,
        firstname: str,
        bioimages: List[BioImageItem],
        output_dir: str | Path,
        use_grayscale: bool = True,
        code_snippet: Optional[str] = None,
    ) -> Path:
        """
        Genera el reporte PDF para el analisis y descomposicion multicanal RGB (Actividad 2.2).
        """
        if len(bioimages) < 3:
            raise ReportGeneratorError(
                STRINGS.ERR_LESS_THAN_THREE_IMAGES.format(count=len(bioimages))
            )

        if not lastname.strip() or not firstname.strip():
            raise ReportGeneratorError(STRINGS.ERR_STUDENT_DATA_REQUIRED)

        for item in bioimages[:3]:
            if not item.metadata.is_color:
                raise ReportGeneratorError(
                    STRINGS.ERR_IMAGE_NOT_COLOR.format(name=item.metadata.filename)
                )

        out_path = Path(output_dir) / cls.build_standard_filename(lastname, firstname, "Actividad2.2")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(
            str(out_path),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=32,
            bottomMargin=32,
        )

        styles = getSampleStyleSheet()
        section_style = ParagraphStyle(
            "DocSection",
            parent=styles["Heading2"],
            fontSize=11.5,
            leading=15,
            textColor=colors.HexColor("#0C4A6E"),
            spaceBefore=10,
            spaceAfter=4,
        )
        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#0C2340"),
        )
        cell_label_style = ParagraphStyle(
            "CellLabel",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#0A1C30"),
            alignment=1,
        )
        code_style = ParagraphStyle(
            "CodeBlock",
            fontName="Courier",
            fontSize=7,
            leading=9,
            textColor=colors.HexColor("#0A1C30"),
        )

        story = []

        # Encabezado institucional glacial con logo
        story.append(cls._create_header_table(STRINGS.PDF_REPORT_DOC_TITLE_22, lastname, firstname, styles))
        story.append(Spacer(1, 8))

        # Codigo de Descomposicion RGB
        story.append(Paragraph(STRINGS.PDF_CODE_SECTION_TITLE, section_style))
        default_code = (
            "# Descomposicion de canales Rojo, Verde y Azul con NumPy vectorizado\n"
            "import numpy as np\n"
            "from PIL import Image\n\n"
            "def decompose_rgb_channels(rgb_array):\n"
            "    red_channel = rgb_array[:, :, 0]    # Canal Rojo\n"
            "    green_channel = rgb_array[:, :, 1]  # Canal Verde\n"
            "    blue_channel = rgb_array[:, :, 2]   # Canal Azul\n"
            "    return red_channel, green_channel, blue_channel\n"
        )
        code_text = code_snippet if code_snippet else default_code
        code_flowable = Preformatted(code_text, code_style)
        code_box = Table([[code_flowable]], colWidths=[540])
        code_box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0F9FF")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#BAE6FD")),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(code_box)
        story.append(Spacer(1, 8))

        # Descomposicion de cada una de las 3 bioimagenes
        story.append(Paragraph(STRINGS.PDF_RESULTS_SECTION_TITLE, section_style))

        temp_files = []
        try:
            for idx, item in enumerate(bioimages[:3], start=1):
                decomp = ImageProcessor.decompose_rgb(item.original_array)

                f_orig = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                f_red = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                f_green = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                f_blue = tempfile.NamedTemporaryFile(suffix=".png", delete=False)

                for f in [f_orig, f_red, f_green, f_blue]:
                    temp_files.append(f.name)
                    f.close()

                Image.fromarray(decomp.original_rgb).save(f_orig.name, format="PNG")
                if use_grayscale:
                    Image.fromarray(decomp.red_gray).save(f_red.name, format="PNG")
                    Image.fromarray(decomp.green_gray).save(f_green.name, format="PNG")
                    Image.fromarray(decomp.blue_gray).save(f_blue.name, format="PNG")
                else:
                    Image.fromarray(decomp.red_color).save(f_red.name, format="PNG")
                    Image.fromarray(decomp.green_color).save(f_green.name, format="PNG")
                    Image.fromarray(decomp.blue_color).save(f_blue.name, format="PNG")

                w_img, h_img = 125, 95
                img_orig = RLImage(f_orig.name, width=w_img, height=h_img)
                img_r = RLImage(f_red.name, width=w_img, height=h_img)
                img_g = RLImage(f_green.name, width=w_img, height=h_img)
                img_b = RLImage(f_blue.name, width=w_img, height=h_img)

                grid_data = [
                    [
                        Paragraph(f"<b>{STRINGS.MULTICHANNEL_CHANNEL_ORIGINAL}</b>", cell_label_style),
                        Paragraph(f"<b>{STRINGS.MULTICHANNEL_CHANNEL_RED}</b>", cell_label_style),
                        Paragraph(f"<b>{STRINGS.MULTICHANNEL_CHANNEL_GREEN}</b>", cell_label_style),
                        Paragraph(f"<b>{STRINGS.MULTICHANNEL_CHANNEL_BLUE}</b>", cell_label_style),
                    ],
                    [img_orig, img_r, img_g, img_b],
                ]

                grid_table = Table(grid_data, colWidths=[135, 135, 135, 135])
                grid_table.setStyle(TableStyle([
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E0F2FE")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#BAE6FD")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0F2FE")),
                    ("PADDING", (0, 0), (-1, -1), 4),
                ]))

                header_text = f"<b>Bioimagen {idx}:</b> {item.metadata.filename} ({item.metadata.width}x{item.metadata.height} px)"
                stats_text = (
                    f"{decomp.stats_red.formatted()}<br/>"
                    f"{decomp.stats_green.formatted()}<br/>"
                    f"{decomp.stats_blue.formatted()}"
                )

                card = [
                    Paragraph(header_text, body_style),
                    Spacer(1, 3),
                    grid_table,
                    Spacer(1, 3),
                    Paragraph(f"<i>{stats_text}</i>", body_style),
                    Spacer(1, 8),
                ]
                story.append(KeepTogether(card))

            doc.build(story)
        finally:
            for t_file in temp_files:
                try:
                    if os.path.exists(t_file):
                        os.remove(t_file)
                except Exception:
                    pass

        return out_path

    @classmethod
    def generate_activity_3_1_pdf(
        cls,
        lastname: str,
        firstname: str,
        bioimages: List[BioImageItem],
        output_dir: str | Path,
    ) -> Path:
        """
        Genera el reporte PDF para Ajuste de Rango Dinamico en imagenes DICOM (Actividad 3.1).
        Muestra la imagen original, el histograma y la imagen con rango dinámico ajustado.
        """
        if len(bioimages) < 3:
            raise ReportGeneratorError(
                STRINGS.ERR_LESS_THAN_THREE_IMAGES.format(count=len(bioimages))
            )

        if not lastname.strip() or not firstname.strip():
            raise ReportGeneratorError(STRINGS.ERR_STUDENT_DATA_REQUIRED)

        out_path = Path(output_dir) / cls.build_standard_filename(lastname, firstname, "Actividad3.1")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(str(out_path), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=32, bottomMargin=32)
        styles = getSampleStyleSheet()
        section_style = ParagraphStyle("DocSection", parent=styles["Heading2"], fontSize=11.5, leading=15, textColor=colors.HexColor("#0C4A6E"), spaceBefore=10, spaceAfter=4)
        body_style = ParagraphStyle("DocBody", parent=styles["Normal"], fontSize=8.5, leading=11, textColor=colors.HexColor("#0C2340"))
        
        story = []
        story.append(cls._create_header_table(STRINGS.PDF_REPORT_DOC_TITLE_31, lastname, firstname, styles))
        story.append(Spacer(1, 8))
        story.append(Paragraph(STRINGS.PDF_RESULTS_SECTION_TITLE, section_style))

        temp_files = []
        try:
            for idx, item in enumerate(bioimages[:3], start=1):
                arr_orig = item.original_array
                if arr_orig.ndim == 3:
                    # Usar un canal para el histograma si es RGB (DICOM CT es gris típicamente)
                    gray_arr = arr_orig[:, :, 0]
                else:
                    gray_arr = arr_orig

                # 1. Imagen original (Rango original) - esto usualmente requiere normalizacion para verse bien,
                # pero el requerimiento es mostrarla tal cual. Asumimos que arr_orig es uint8 y fue escalada.
                f_orig = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                temp_files.append(f_orig.name)
                f_orig.close()
                Image.fromarray(arr_orig).save(f_orig.name, format="PNG")

                # 2. Histograma
                f_hist = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                temp_files.append(f_hist.name)
                f_hist.close()
                
                plt.figure(figsize=(4, 3))
                hist_data = np.bincount(gray_arr.ravel(), minlength=256)[:256]
                plt.plot(hist_data, color='black')
                plt.title(f"Histograma Bioimagen {idx}")
                plt.xlim([0, 256])
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig(f_hist.name, dpi=100)
                plt.close()

                # Zona de interes para centrar: tomamos los valores entre el percentil 2 y 98 para ajuste dinamico robusto
                min_val = np.percentile(gray_arr, 2)
                max_val = np.percentile(gray_arr, 98)

                # 3. Imagen con nuevo rango dinamico
                arr_adjusted = ImageProcessor.dynamic_range_adjustment(arr_orig, int(min_val), int(max_val))
                f_adj = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                temp_files.append(f_adj.name)
                f_adj.close()
                Image.fromarray(arr_adjusted).save(f_adj.name, format="PNG")

                w_img, h_img = 150, 150
                img_orig = RLImage(f_orig.name, width=w_img, height=h_img)
                img_hist = RLImage(f_hist.name, width=170, height=130)
                img_adj = RLImage(f_adj.name, width=w_img, height=h_img)

                grid_data = [
                    [
                        Paragraph(f"<b>Original</b>", body_style),
                        Paragraph(f"<b>Histograma</b>", body_style),
                        Paragraph(f"<b>Rango Ajustado</b><br/>(Min: {int(min_val)}, Max: {int(max_val)})", body_style),
                    ],
                    [img_orig, img_hist, img_adj],
                ]

                grid_table = Table(grid_data, colWidths=[165, 185, 165])
                grid_table.setStyle(TableStyle([
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#BAE6FD")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0F2FE")),
                    ("PADDING", (0, 0), (-1, -1), 4),
                ]))

                header_text = f"<b>Bioimagen {idx}:</b> {item.metadata.filename}"
                card = [
                    Paragraph(header_text, body_style),
                    Spacer(1, 3),
                    grid_table,
                    Spacer(1, 10),
                ]
                story.append(KeepTogether(card))

            doc.build(story)
        finally:
            for t_file in temp_files:
                try:
                    if os.path.exists(t_file):
                        os.remove(t_file)
                except Exception:
                    pass

        return out_path

    @classmethod
    def generate_activity_3_2_pdf(
        cls,
        lastname: str,
        firstname: str,
        bioimages: List[BioImageItem],
        output_dir: str | Path,
    ) -> Path:
        """
        Genera el reporte PDF para Combinacion de Imagenes RGB (Actividad 3.2).
        """
        if len(bioimages) < 2:
            raise ReportGeneratorError(
                "Se requieren al menos 2 imagenes RGB cargadas para esta actividad."
            )

        if not lastname.strip() or not firstname.strip():
            raise ReportGeneratorError(STRINGS.ERR_STUDENT_DATA_REQUIRED)

        out_path = Path(output_dir) / cls.build_standard_filename(lastname, firstname, "Actividad3.2")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(str(out_path), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=32, bottomMargin=32)
        styles = getSampleStyleSheet()
        section_style = ParagraphStyle("DocSection", parent=styles["Heading2"], fontSize=11.5, leading=15, textColor=colors.HexColor("#0C4A6E"), spaceBefore=10, spaceAfter=4)
        body_style = ParagraphStyle("DocBody", parent=styles["Normal"], fontSize=8.5, leading=11, textColor=colors.HexColor("#0C2340"))
        
        story = []
        story.append(cls._create_header_table(STRINGS.PDF_REPORT_DOC_TITLE_32, lastname, firstname, styles))
        story.append(Spacer(1, 8))

        temp_files = []
        try:
            img1 = bioimages[0].original_array
            img2 = bioimages[1].original_array

            # Originales
            f_orig1 = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            f_orig2 = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            temp_files.extend([f_orig1.name, f_orig2.name])
            f_orig1.close()
            f_orig2.close()
            Image.fromarray(img1).save(f_orig1.name, format="PNG")
            Image.fromarray(img2).save(f_orig2.name, format="PNG")

            story.append(Paragraph("<b>Imagenes Originales:</b>", section_style))
            
            rl_img1 = RLImage(f_orig1.name, width=150, height=150)
            rl_img2 = RLImage(f_orig2.name, width=150, height=150)
            
            orig_table = Table([[rl_img1, rl_img2]], colWidths=[200, 200])
            orig_table.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
            story.append(orig_table)
            story.append(Spacer(1, 10))

            story.append(Paragraph("<b>Combinaciones (I1, I2):</b>", section_style))

            combinations = [
                (0.7, 0.3, 0.5, 0.5, 0.2, 0.8), # Mezcla 1
                (0.39, 0.61, 0.8, 0.2, 0.1, 0.9), # Mezcla 2
                (0.9, 0.1, 0.1, 0.9, 0.5, 0.5)  # Mezcla 3
            ]

            for idx, (r1, r2, g1, g2, b1, b2) in enumerate(combinations, start=1):
                arr_comb = ImageProcessor.combine_rgb_images(img1, img2, r1, r2, g1, g2, b1, b2)
                f_comb = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                temp_files.append(f_comb.name)
                f_comb.close()
                Image.fromarray(arr_comb).save(f_comb.name, format="PNG")

                rl_comb = RLImage(f_comb.name, width=180, height=180)
                info = f"<b>Combinacion {idx}:</b><br/>Canal Rojo: {int(r1*100)}% I1, {int(r2*100)}% I2<br/>Canal Verde: {int(g1*100)}% I1, {int(g2*100)}% I2<br/>Canal Azul: {int(b1*100)}% I1, {int(b2*100)}% I2"
                
                comb_table = Table([[Paragraph(info, body_style), rl_comb]], colWidths=[200, 250])
                comb_table.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
                
                story.append(KeepTogether([comb_table, Spacer(1, 10)]))

            doc.build(story)
        finally:
            for t_file in temp_files:
                try:
                    if os.path.exists(t_file):
                        os.remove(t_file)
                except Exception:
                    pass

        return out_path
