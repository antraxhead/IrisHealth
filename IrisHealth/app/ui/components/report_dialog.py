"""
Dialogo para parametrizacion y generacion de reportes PDF clinicos y academicos.
Permite configurar el nombre del autor y seleccionar la modalidad de analisis.
Incorpora la paleta glacial y el logotipo institucional de forma dinamica sin rutas hardcodeadas.
Cumple con la regla de cero strings hardcodeadas y cero emojis.
"""

from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QFileDialog,
    QMessageBox,
)

from app.constants.strings import STRINGS
from app.constants.paths import get_logo_path, get_default_reports_dir
from app.core.bioimage_reader import BioImageItem
from app.core.report_generator import ReportGenerator, ReportGeneratorError
from app.ui.styles import MAIN_STYLESHEET


class ReportDialog(QDialog):
    """Ventana de dialogo para la exportacion de reportes PDF."""

    def __init__(self, bioimages: List[BioImageItem], parent: Optional[QDialog] = None):
        super().__init__(parent)
        self._bioimages = bioimages
        self.setWindowTitle(STRINGS.PDF_DIALOG_TITLE)
        self.setMinimumWidth(500)
        self.setStyleSheet(MAIN_STYLESHEET)

        # Configurar icono institucional dinamicamente
        logo_path = get_logo_path()
        if logo_path.exists():
            self.setWindowIcon(QIcon(str(logo_path)))

        self._setup_ui()
        self._update_preview()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)

        # Encabezado glacial con logotipo institucional
        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)

        logo_path = get_logo_path()
        if logo_path.exists():
            logo_label = QLabel(self)
            pix = QPixmap(str(logo_path)).scaled(
                46, 46,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_label.setPixmap(pix)
            header_layout.addWidget(logo_label)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)
        header_label = QLabel(STRINGS.PDF_DIALOG_HEADER, self)
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #0A1C30;")
        sub_label = QLabel(STRINGS.PDF_REPORT_INSTITUTION, self)
        sub_label.setStyleSheet("font-size: 11px; color: #0284C7; font-weight: 600;")
        title_vbox.addWidget(header_label)
        title_vbox.addWidget(sub_label)
        header_layout.addLayout(title_vbox)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Separador glacial
        sep = QLabel(self)
        sep.setFixedHeight(2)
        sep.setStyleSheet("background-color: #BAE6FD;")
        layout.addWidget(sep)

        # Campos de texto
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)

        lbl_last = QLabel(STRINGS.PDF_LABEL_LASTNAME, self)
        lbl_last.setStyleSheet("font-weight: 600; color: #0C4A6E;")
        self._input_lastname = QLineEdit(self)
        self._input_lastname.setPlaceholderText("Ejemplo: Mendizabal")
        self._input_lastname.textChanged.connect(self._update_preview)
        form_layout.addWidget(lbl_last)
        form_layout.addWidget(self._input_lastname)

        lbl_first = QLabel(STRINGS.PDF_LABEL_FIRSTNAME, self)
        lbl_first.setStyleSheet("font-weight: 600; color: #0C4A6E;")
        self._input_firstname = QLineEdit(self)
        self._input_firstname.setPlaceholderText("Ejemplo: Eduardo")
        self._input_firstname.textChanged.connect(self._update_preview)
        form_layout.addWidget(lbl_first)
        form_layout.addWidget(self._input_firstname)

        lbl_act = QLabel(STRINGS.PDF_LABEL_ACTIVITY, self)
        lbl_act.setStyleSheet("font-weight: 600; color: #0C4A6E;")
        self._combo_activity = QComboBox(self)
        self._combo_activity.addItem(STRINGS.PDF_OPTION_SERIES, "Actividad2.1")
        self._combo_activity.addItem(STRINGS.PDF_OPTION_RGB, "Actividad2.2")
        self._combo_activity.addItem(STRINGS.PDF_OPTION_DICOM, "Actividad3.1")
        self._combo_activity.addItem(STRINGS.PDF_OPTION_COMBINE, "Actividad3.2")
        self._combo_activity.currentIndexChanged.connect(self._update_preview)
        form_layout.addWidget(lbl_act)
        form_layout.addWidget(self._combo_activity)

        # Directorio de salida con ruta dinamica
        lbl_out = QLabel(STRINGS.PDF_LABEL_OUTPUT_DIR, self)
        lbl_out.setStyleSheet("font-weight: 600; color: #0C4A6E;")
        out_layout = QHBoxLayout()
        default_dir = str(get_default_reports_dir())
        self._input_output_dir = QLineEdit(default_dir, self)
        self._btn_browse = QPushButton(STRINGS.BTN_BROWSE, self)
        self._btn_browse.setObjectName("btn_secondary")
        self._btn_browse.clicked.connect(self._on_browse_dir)
        out_layout.addWidget(self._input_output_dir)
        out_layout.addWidget(self._btn_browse)
        form_layout.addWidget(lbl_out)
        form_layout.addLayout(out_layout)

        layout.addLayout(form_layout)

        # Previsualizacion del nombre del archivo oficial en caja glacial
        self._lbl_preview = QLabel(self)
        self._lbl_preview.setStyleSheet(
            "background-color: #E0F2FE; border: 1px solid #BAE6FD; border-radius: 5px; padding: 10px; color: #0369A1; font-weight: 600;"
        )
        layout.addWidget(self._lbl_preview)

        # Botones de accion
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self._btn_cancel = QPushButton(STRINGS.BTN_CANCEL, self)
        self._btn_cancel.setObjectName("btn_secondary")
        self._btn_cancel.clicked.connect(self.reject)

        self._btn_generate = QPushButton(STRINGS.PDF_BTN_GENERATE, self)
        self._btn_generate.clicked.connect(self._on_generate)

        btn_layout.addWidget(self._btn_cancel)
        btn_layout.addWidget(self._btn_generate)
        layout.addLayout(btn_layout)

    def _update_preview(self) -> None:
        """Actualiza la etiqueta con la vista previa del nombre de archivo estandarizado."""
        last = self._input_lastname.text().strip() or "Primerapellido"
        first = self._input_firstname.text().strip() or "primerNombre"
        act_code = self._combo_activity.currentData()
        fname = ReportGenerator.build_standard_filename(last, first, act_code)
        self._lbl_preview.setText(f"{STRINGS.PDF_LABEL_PREVIEW_FILENAME} {fname}")

    def _on_browse_dir(self) -> None:
        """Abre un explorador para seleccionar carpeta de destino."""
        selected = QFileDialog.getExistingDirectory(
            self,
            STRINGS.FILE_DIALOG_OPEN_FOLDER,
            self._input_output_dir.text()
        )
        if selected:
            self._input_output_dir.setText(selected)

    def _on_generate(self) -> None:
        """Valida y ejecuta la creacion del reporte en formato PDF."""
        lastname = self._input_lastname.text().strip()
        firstname = self._input_firstname.text().strip()
        out_dir = self._input_output_dir.text().strip()
        act_code = self._combo_activity.currentData()

        if not lastname or not firstname:
            QMessageBox.warning(self, STRINGS.WARN_TITLE, STRINGS.ERR_STUDENT_DATA_REQUIRED)
            return

        if len(self._bioimages) < 3:
            msg = STRINGS.ERR_LESS_THAN_THREE_IMAGES.format(count=len(self._bioimages))
            QMessageBox.warning(self, STRINGS.WARN_TITLE, msg)
            return

        try:
            if act_code == "Actividad2.1":
                res_path = ReportGenerator.generate_activity_2_1_pdf(
                    lastname=lastname,
                    firstname=firstname,
                    bioimages=self._bioimages,
                    output_dir=out_dir,
                )
            elif act_code == "Actividad2.2":
                res_path = ReportGenerator.generate_activity_2_2_pdf(
                    lastname=lastname,
                    firstname=firstname,
                    bioimages=self._bioimages,
                    output_dir=out_dir,
                )
            elif act_code == "Actividad3.1":
                res_path = ReportGenerator.generate_activity_3_1_pdf(
                    lastname=lastname,
                    firstname=firstname,
                    bioimages=self._bioimages,
                    output_dir=out_dir,
                )
            elif act_code == "Actividad3.2":
                res_path = ReportGenerator.generate_activity_3_2_pdf(
                    lastname=lastname,
                    firstname=firstname,
                    bioimages=self._bioimages,
                    output_dir=out_dir,
                )
            else:
                raise ReportGeneratorError(f"Actividad no implementada: {act_code}")

            QMessageBox.information(
                self,
                STRINGS.PDF_SUCCESS_TITLE,
                STRINGS.PDF_SUCCESS_MESSAGE.format(filepath=str(res_path))
            )
            self.accept()

        except ReportGeneratorError as rge:
            QMessageBox.critical(self, STRINGS.ERR_TITLE, str(rge))
        except Exception as ex:
            msg = STRINGS.ERR_PDF_GENERATION_FAILED.format(reason=str(ex))
            QMessageBox.critical(self, STRINGS.ERR_TITLE, msg)
