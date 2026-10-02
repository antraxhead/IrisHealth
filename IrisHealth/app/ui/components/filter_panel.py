"""
Panel de control de filtros, fases y rango dinamico con estetica Liquid Glass.
Emite senales de actualizacion en tiempo real hacia el lienzo de visualizacion.
Totalmente desacoplado de strings quemadas y sin emojis.
"""

from typing import Dict, Any, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QSlider,
    QComboBox,
    QPushButton,
    QScrollArea,
)

from app.constants.strings import STRINGS
from app.ui.components.histogram_widget import HistogramWidget


class FilterPanel(QWidget):
    """Estacion de filtrado y control de fases multicanal."""

    pipeline_changed = Signal(dict)
    reset_requested = Signal()
    export_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        # 1. Grupo Luminancia
        grp_lum = QGroupBox(STRINGS.FILTER_GROUP_LUMINANCE, container)
        lay_lum = QVBoxLayout(grp_lum)
        lay_lum.setSpacing(6)

        # Brillo
        self._lbl_bright = QLabel(STRINGS.FILTER_LABEL_BRIGHTNESS.format(val=0), grp_lum)
        self._slider_bright = QSlider(Qt.Orientation.Horizontal, grp_lum)
        self._slider_bright.setRange(-100, 100)
        self._slider_bright.setValue(0)
        self._slider_bright.valueChanged.connect(self._on_values_changed)
        lay_lum.addWidget(self._lbl_bright)
        lay_lum.addWidget(self._slider_bright)

        # Contraste
        self._lbl_contrast = QLabel(STRINGS.FILTER_LABEL_CONTRAST.format(val=1.0), grp_lum)
        self._slider_contrast = QSlider(Qt.Orientation.Horizontal, grp_lum)
        self._slider_contrast.setRange(20, 300)
        self._slider_contrast.setValue(100)
        self._slider_contrast.valueChanged.connect(self._on_values_changed)
        lay_lum.addWidget(self._lbl_contrast)
        lay_lum.addWidget(self._slider_contrast)

        # Gamma
        self._lbl_gamma = QLabel(STRINGS.FILTER_LABEL_GAMMA.format(val=1.0), grp_lum)
        self._slider_gamma = QSlider(Qt.Orientation.Horizontal, grp_lum)
        self._slider_gamma.setRange(20, 300)
        self._slider_gamma.setValue(100)
        self._slider_gamma.valueChanged.connect(self._on_values_changed)
        lay_lum.addWidget(self._lbl_gamma)
        lay_lum.addWidget(self._slider_gamma)

        layout.addWidget(grp_lum)

        # 2. Grupo Fases de Color
        grp_phase = QGroupBox(STRINGS.FILTER_GROUP_COLOR_PHASE, container)
        lay_phase = QVBoxLayout(grp_phase)
        lay_phase.setSpacing(6)

        # Fase R
        self._lbl_phase_r = QLabel(STRINGS.FILTER_LABEL_PHASE_RED.format(val=1.0), grp_phase)
        self._slider_phase_r = QSlider(Qt.Orientation.Horizontal, grp_phase)
        self._slider_phase_r.setRange(0, 200)
        self._slider_phase_r.setValue(100)
        self._slider_phase_r.valueChanged.connect(self._on_values_changed)
        lay_phase.addWidget(self._lbl_phase_r)
        lay_phase.addWidget(self._slider_phase_r)

        # Fase G
        self._lbl_phase_g = QLabel(STRINGS.FILTER_LABEL_PHASE_GREEN.format(val=1.0), grp_phase)
        self._slider_phase_g = QSlider(Qt.Orientation.Horizontal, grp_phase)
        self._slider_phase_g.setRange(0, 200)
        self._slider_phase_g.setValue(100)
        self._slider_phase_g.valueChanged.connect(self._on_values_changed)
        lay_phase.addWidget(self._lbl_phase_g)
        lay_phase.addWidget(self._slider_phase_g)

        # Fase B
        self._lbl_phase_b = QLabel(STRINGS.FILTER_LABEL_PHASE_BLUE.format(val=1.0), grp_phase)
        self._slider_phase_b = QSlider(Qt.Orientation.Horizontal, grp_phase)
        self._slider_phase_b.setRange(0, 200)
        self._slider_phase_b.setValue(100)
        self._slider_phase_b.valueChanged.connect(self._on_values_changed)
        lay_phase.addWidget(self._lbl_phase_b)
        lay_phase.addWidget(self._slider_phase_b)

        layout.addWidget(grp_phase)

        # 3. Filtros Espaciales
        grp_spatial = QGroupBox(STRINGS.FILTER_GROUP_SPATIAL, container)
        lay_spatial = QVBoxLayout(grp_spatial)
        self._combo_spatial = QComboBox(grp_spatial)
        self._combo_spatial.addItem(STRINGS.FILTER_SPATIAL_NONE, "none")
        self._combo_spatial.addItem(STRINGS.FILTER_SPATIAL_SHARPEN, "sharpen")
        self._combo_spatial.addItem(STRINGS.FILTER_SPATIAL_BLUR, "blur")
        self._combo_spatial.addItem(STRINGS.FILTER_SPATIAL_SOBEL, "sobel")
        self._combo_spatial.addItem(STRINGS.FILTER_SPATIAL_INVERT, "invert")
        self._combo_spatial.currentIndexChanged.connect(self._on_values_changed)
        lay_spatial.addWidget(self._combo_spatial)
        layout.addWidget(grp_spatial)

        # 4. Mapas de Pseudocolor (LUT)
        grp_lut = QGroupBox(STRINGS.FILTER_GROUP_LUT, container)
        lay_lut = QVBoxLayout(grp_lut)
        self._combo_lut = QComboBox(grp_lut)
        self._combo_lut.addItem(STRINGS.LUT_NATURAL, "natural")
        self._combo_lut.addItem(STRINGS.LUT_GRAYSCALE, "grayscale")
        self._combo_lut.addItem(STRINGS.LUT_FLUORESCENCE, "fluorescence")
        self._combo_lut.addItem(STRINGS.LUT_THERMAL, "thermal")
        self._combo_lut.currentIndexChanged.connect(self._on_values_changed)
        lay_lut.addWidget(self._combo_lut)
        layout.addWidget(grp_lut)

        # 5. Histograma Espectral
        self._histogram_widget = HistogramWidget(container)
        layout.addWidget(self._histogram_widget)

        # 6. Botones de Accion
        btn_layout = QHBoxLayout()
        self._btn_reset = QPushButton(STRINGS.BTN_RESET_FILTERS, container)
        self._btn_reset.setObjectName("btn_secondary")
        self._btn_reset.clicked.connect(self.reset_filters)

        self._btn_export = QPushButton(STRINGS.TOOL_EXPORT_PROCESSED, container)
        self._btn_export.setObjectName("btn_accent")
        self._btn_export.clicked.connect(self.export_requested.emit)

        btn_layout.addWidget(self._btn_reset)
        btn_layout.addWidget(self._btn_export)
        layout.addLayout(btn_layout)

        scroll.setWidget(container)
        outer_layout.addWidget(scroll)

    def get_pipeline_params(self) -> Dict[str, Any]:
        """Devuelve el diccionario completo de parametros actuales."""
        bright = self._slider_bright.value()
        contrast = self._slider_contrast.value() / 100.0
        gamma = self._slider_gamma.value() / 100.0
        phase_r = self._slider_phase_r.value() / 100.0
        phase_g = self._slider_phase_g.value() / 100.0
        phase_b = self._slider_phase_b.value() / 100.0
        spatial = self._combo_spatial.currentData()
        lut = self._combo_lut.currentData()

        return {
            "brightness": bright,
            "contrast": contrast,
            "gamma": gamma,
            "phase_red": phase_r,
            "phase_green": phase_g,
            "phase_blue": phase_b,
            "spatial_filter": spatial,
            "lut_mode": lut,
        }

    def _on_values_changed(self) -> None:
        """Actualiza etiquetas e informa a los observadores sobre el cambio."""
        params = self.get_pipeline_params()
        self._lbl_bright.setText(STRINGS.FILTER_LABEL_BRIGHTNESS.format(val=params["brightness"]))
        self._lbl_contrast.setText(STRINGS.FILTER_LABEL_CONTRAST.format(val=params["contrast"]))
        self._lbl_gamma.setText(STRINGS.FILTER_LABEL_GAMMA.format(val=params["gamma"]))
        self._lbl_phase_r.setText(STRINGS.FILTER_LABEL_PHASE_RED.format(val=params["phase_red"]))
        self._lbl_phase_g.setText(STRINGS.FILTER_LABEL_PHASE_GREEN.format(val=params["phase_green"]))
        self._lbl_phase_b.setText(STRINGS.FILTER_LABEL_PHASE_BLUE.format(val=params["phase_blue"]))

        self.pipeline_changed.emit(params)

    def reset_filters(self) -> None:
        """Restablece todos los controladores a sus valores neutros por defecto."""
        self.blockSignals(True)
        self._slider_bright.setValue(0)
        self._slider_contrast.setValue(100)
        self._slider_gamma.setValue(100)
        self._slider_phase_r.setValue(100)
        self._slider_phase_g.setValue(100)
        self._slider_phase_b.setValue(100)
        self._combo_spatial.setCurrentIndex(0)
        self._combo_lut.setCurrentIndex(0)
        self.blockSignals(False)
        self._on_values_changed()
        self.reset_requested.emit()

    def update_histogram(self, hist_data: Optional[Dict[str, Any]]) -> None:
        """Transmite los datos calculados de intensidad al widget de histograma."""
        self._histogram_widget.set_histogram_data(hist_data)
