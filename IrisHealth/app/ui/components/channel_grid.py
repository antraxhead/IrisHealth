"""
Componente de cuadricula 2x2 para la descomposicion de canales RGB con maxima optimizacion espacial.
Despliega simultaneamente la imagen original y los canales Rojo, Verde y Azul.
Integra cinta horizontal de metricas cuantitativas en 3 columnas y sincronizacion de sonda clinica.
Estricto apego a Liquid Glass, sin cadenas hardcodeadas ni emojis.
"""

from typing import Optional
import numpy as np

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
)

from app.constants.strings import STRINGS
from app.core.bioimage_reader import BioImageItem
from app.core.image_processor import ImageProcessor, RGBDecompositionResult
from app.ui.components.image_canvas import ImageCanvas


class ChannelGrid(QWidget):
    """Cuadricula 2x2 interactiva para analisis espectral y multicanal con tematica glacial."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._current_decomp: Optional[RGBDecompositionResult] = None
        self._use_grayscale: bool = True
        self._layout_mode: str = "2x2"

        self._setup_ui()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 2, 0, 0)
        main_layout.setSpacing(6)

        # Lienzos clinicos de maxima superficie con insignias de canal estilo Color Separation
        self._grid_layout = QGridLayout()
        self._grid_layout.setSpacing(6)

        self._canvas_orig = ImageCanvas(title=STRINGS.MULTICHANNEL_CHANNEL_ORIGINAL, parent=self)
        self._canvas_red = ImageCanvas(title=STRINGS.MULTICHANNEL_CHANNEL_RED, parent=self)
        self._canvas_green = ImageCanvas(title=STRINGS.MULTICHANNEL_CHANNEL_GREEN, parent=self)
        self._canvas_blue = ImageCanvas(title=STRINGS.MULTICHANNEL_CHANNEL_BLUE, parent=self)

        # Desactivar actualizacion automatica local para sincronizacion centralizada exacta
        self._canvas_orig.set_auto_hud_probe(False)
        self._canvas_red.set_auto_hud_probe(False)
        self._canvas_green.set_auto_hud_probe(False)
        self._canvas_blue.set_auto_hud_probe(False)

        # Sincronizacion cruzada de sonda clinica entre los 4 cuadrantes
        self._canvas_orig.pixel_probed.connect(self._on_pixel_probed)
        self._canvas_red.pixel_probed.connect(self._on_pixel_probed)
        self._canvas_green.pixel_probed.connect(self._on_pixel_probed)
        self._canvas_blue.pixel_probed.connect(self._on_pixel_probed)

        # Crear celdas con insignias de canal (badges) al pie estilo Color Separation
        self._cell_orig = self._create_channel_cell(self._canvas_orig, STRINGS.MULTICHANNEL_BADGE_ORIGINAL, "badge_channel_orig")
        self._cell_red = self._create_channel_cell(self._canvas_red, STRINGS.MULTICHANNEL_BADGE_RED, "badge_channel_red")
        self._cell_green = self._create_channel_cell(self._canvas_green, STRINGS.MULTICHANNEL_BADGE_GREEN, "badge_channel_green")
        self._cell_blue = self._create_channel_cell(self._canvas_blue, STRINGS.MULTICHANNEL_BADGE_BLUE, "badge_channel_blue")

        self._apply_grid_layout()

        main_layout.addLayout(self._grid_layout, stretch=1)

        # Cinta Horizontal Compacta de Metricas Cuantitativas por Canal (3 columnas)
        stats_panel = QFrame(self)
        stats_panel.setObjectName("stats_horizontal_panel")
        stats_panel.setFixedHeight(36)
        stats_layout = QHBoxLayout(stats_panel)
        stats_layout.setContentsMargins(6, 3, 6, 3)
        stats_layout.setSpacing(8)

        # Tarjeta Canal Rojo (Banda R - 630 nm)
        card_r = QFrame(stats_panel)
        card_r.setObjectName("stats_card_red")
        layout_r = QHBoxLayout(card_r)
        layout_r.setContentsMargins(8, 2, 8, 2)
        layout_r.setSpacing(6)
        lbl_title_r = QLabel(STRINGS.MULTICHANNEL_LABEL_BAND_R, card_r)
        lbl_title_r.setObjectName("stats_card_title_r")
        self._label_stats_r = QLabel("-", card_r)
        self._label_stats_r.setObjectName("stats_card_val")
        layout_r.addWidget(lbl_title_r)
        layout_r.addWidget(self._label_stats_r, stretch=1)
        stats_layout.addWidget(card_r, stretch=1)

        # Tarjeta Canal Verde (Banda G - 520 nm)
        card_g = QFrame(stats_panel)
        card_g.setObjectName("stats_card_green")
        layout_g = QHBoxLayout(card_g)
        layout_g.setContentsMargins(8, 2, 8, 2)
        layout_g.setSpacing(6)
        lbl_title_g = QLabel(STRINGS.MULTICHANNEL_LABEL_BAND_G, card_g)
        lbl_title_g.setObjectName("stats_card_title_g")
        self._label_stats_g = QLabel("-", card_g)
        self._label_stats_g.setObjectName("stats_card_val")
        layout_g.addWidget(lbl_title_g)
        layout_g.addWidget(self._label_stats_g, stretch=1)
        stats_layout.addWidget(card_g, stretch=1)

        # Tarjeta Canal Azul (Banda B - 450 nm)
        card_b = QFrame(stats_panel)
        card_b.setObjectName("stats_card_blue")
        layout_b = QHBoxLayout(card_b)
        layout_b.setContentsMargins(8, 2, 8, 2)
        layout_b.setSpacing(6)
        lbl_title_b = QLabel(STRINGS.MULTICHANNEL_LABEL_BAND_B, card_b)
        lbl_title_b.setObjectName("stats_card_title_b")
        self._label_stats_b = QLabel("-", card_b)
        self._label_stats_b.setObjectName("stats_card_val")
        layout_b.addWidget(lbl_title_b)
        layout_b.addWidget(self._label_stats_b, stretch=1)
        stats_layout.addWidget(card_b, stretch=1)

        main_layout.addWidget(stats_panel)

    def _create_channel_cell(self, canvas: ImageCanvas, badge_text: str, badge_obj_name: str) -> QWidget:
        """Encapsula un lienzo con su respectiva insignia cromatica identificadora al pie."""
        cell = QWidget(self)
        cell_layout = QVBoxLayout(cell)
        cell_layout.setContentsMargins(0, 0, 0, 0)
        cell_layout.setSpacing(4)
        cell_layout.addWidget(canvas, stretch=1)

        badge_bar = QHBoxLayout()
        badge_bar.setContentsMargins(0, 0, 0, 0)
        badge_bar.setSpacing(0)
        badge_bar.addStretch()
        badge = QLabel(badge_text, cell)
        badge.setObjectName(badge_obj_name)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_bar.addWidget(badge)
        badge_bar.addStretch()
        cell_layout.addLayout(badge_bar)
        return cell

    def _apply_grid_layout(self) -> None:
        """Aplica la disposicion de celdas segun el modo actual (2x2 o 1x4 horizontal)."""
        self._grid_layout.removeWidget(self._cell_orig)
        self._grid_layout.removeWidget(self._cell_red)
        self._grid_layout.removeWidget(self._cell_green)
        self._grid_layout.removeWidget(self._cell_blue)

        if self._layout_mode == "1x4":
            self._grid_layout.addWidget(self._cell_orig, 0, 0)
            self._grid_layout.addWidget(self._cell_red, 0, 1)
            self._grid_layout.addWidget(self._cell_green, 0, 2)
            self._grid_layout.addWidget(self._cell_blue, 0, 3)
        else:  # "2x2"
            self._grid_layout.addWidget(self._cell_orig, 0, 0)
            self._grid_layout.addWidget(self._cell_red, 0, 1)
            self._grid_layout.addWidget(self._cell_green, 1, 0)
            self._grid_layout.addWidget(self._cell_blue, 1, 1)

    def set_layout_mode(self, mode: str) -> None:
        """Conmuta dinamicamente la disposicion entre '2x2' y '1x4'."""
        if mode in ("2x2", "1x4") and mode != self._layout_mode:
            self._layout_mode = mode
            self._apply_grid_layout()
            self.fit_all_canvases()

    def load_bioimage(self, item: Optional[BioImageItem]) -> None:
        """Procesa y despliega los canales de la bioimagen especificada."""
        if item is None:
            self.clear()
            return

        self._current_decomp = ImageProcessor.decompose_rgb(item.original_array)
        self._canvas_orig.set_numpy_array(self._current_decomp.original_rgb)

        # Actualizar estadisticas cuantitativas en formato compacto
        self._label_stats_r.setText(self._current_decomp.stats_red.formatted_short())
        self._label_stats_g.setText(self._current_decomp.stats_green.formatted_short())
        self._label_stats_b.setText(self._current_decomp.stats_blue.formatted_short())

        self._refresh_channels()

    def clear(self) -> None:
        """Limpia todos los lienzos y etiquetas de estadisticas."""
        self._current_decomp = None
        self._canvas_orig.clear()
        self._canvas_red.clear()
        self._canvas_green.clear()
        self._canvas_blue.clear()
        self._canvas_orig.set_hud_text(STRINGS.HUD_PROBE_IDLE)
        self._canvas_red.set_hud_text(STRINGS.HUD_PROBE_IDLE)
        self._canvas_green.set_hud_text(STRINGS.HUD_PROBE_IDLE)
        self._canvas_blue.set_hud_text(STRINGS.HUD_PROBE_IDLE)
        self._label_stats_r.setText("-")
        self._label_stats_g.setText("-")
        self._label_stats_b.setText("-")

    def fit_all_canvases(self) -> None:
        """Ajusta y centra todas las vistas multicanal simultaneamente."""
        self._canvas_orig.fit_to_window()
        self._canvas_red.fit_to_window()
        self._canvas_green.fit_to_window()
        self._canvas_blue.fit_to_window()

    def on_mode_toggled(self, button_id: int, checked: bool) -> None:
        """Gestiona el cambio de modo entre escala de grises y color."""
        if checked:
            self._use_grayscale = (button_id == 0)
            self._refresh_channels()

    def _on_mode_changed(self, button_id: int, checked: bool) -> None:
        """Metodo de compatibilidad para conmutacion de modo."""
        self.on_mode_toggled(button_id, checked)

    def _on_pixel_probed(self, x: int, y: int, r: int, g: int, b: int) -> None:
        """Sincroniza la lectura de sonda en los 4 cuadrantes con los valores reales del tejido."""
        if self._current_decomp is not None:
            orig = self._current_decomp.original_rgb
            h, w = orig.shape[:2]
            if 0 <= y < h and 0 <= x < w:
                r_val = int(orig[y, x, 0])
                g_val = int(orig[y, x, 1])
                b_val = int(orig[y, x, 2])
            else:
                r_val, g_val, b_val = r, g, b
        else:
            r_val, g_val, b_val = r, g, b

        lum = int(0.299 * r_val + 0.587 * g_val + 0.114 * b_val)
        self._canvas_orig.set_hud_text(STRINGS.HUD_PROBE_TEXT.format(x=x, y=y, r=r_val, g=g_val, b=b_val, lum=lum))
        self._canvas_red.set_hud_text(STRINGS.MULTICHANNEL_PROBE_BAND_FORMAT.format(x=x, y=y, band="R (630 nm)", val=r_val))
        self._canvas_green.set_hud_text(STRINGS.MULTICHANNEL_PROBE_BAND_FORMAT.format(x=x, y=y, band="G (520 nm)", val=g_val))
        self._canvas_blue.set_hud_text(STRINGS.MULTICHANNEL_PROBE_BAND_FORMAT.format(x=x, y=y, band="B (450 nm)", val=b_val))

    def _refresh_channels(self) -> None:
        """Actualiza la visualizacion de los canales segun el modo actual."""
        if self._current_decomp is None:
            return

        if self._use_grayscale:
            self._canvas_red.set_numpy_array(self._current_decomp.red_gray)
            self._canvas_green.set_numpy_array(self._current_decomp.green_gray)
            self._canvas_blue.set_numpy_array(self._current_decomp.blue_gray)
        else:
            self._canvas_red.set_numpy_array(self._current_decomp.red_color)
            self._canvas_green.set_numpy_array(self._current_decomp.green_color)
            self._canvas_blue.set_numpy_array(self._current_decomp.blue_color)
