"""
Widget de histograma espectral con estetica Liquid Glass.
Renderiza curvas antialiasing para los canales R, G, B y Luminancia.
Sin cadenas hardcodeadas y sin emojis.
"""

from typing import Dict, Optional
import numpy as np

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel

from app.constants.strings import STRINGS


class HistogramWidget(QWidget):
    """Lienzo para dibujo vectorial del histograma de intensidades multicanal."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setMinimumHeight(110)
        self.setMaximumHeight(150)
        self._data: Optional[Dict[str, np.ndarray]] = None

        self._show_r = True
        self._show_g = True
        self._show_b = True
        self._show_lum = False

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        controls = QHBoxLayout()
        controls.setSpacing(10)

        title = QLabel(STRINGS.HISTOGRAM_TITLE, self)
        title.setStyleSheet("font-size: 11px; font-weight: bold; color: #0284C7;")
        controls.addWidget(title)
        controls.addStretch()

        self._cb_r = QCheckBox("R", self)
        self._cb_r.setChecked(True)
        self._cb_r.setStyleSheet("color: #DC2626; font-weight: bold; font-size: 10px;")
        self._cb_r.toggled.connect(self._on_toggled)

        self._cb_g = QCheckBox("G", self)
        self._cb_g.setChecked(True)
        self._cb_g.setStyleSheet("color: #059669; font-weight: bold; font-size: 10px;")
        self._cb_g.toggled.connect(self._on_toggled)

        self._cb_b = QCheckBox("B", self)
        self._cb_b.setChecked(True)
        self._cb_b.setStyleSheet("color: #0284C7; font-weight: bold; font-size: 10px;")
        self._cb_b.toggled.connect(self._on_toggled)

        controls.addWidget(self._cb_r)
        controls.addWidget(self._cb_g)
        controls.addWidget(self._cb_b)

        layout.addLayout(controls)

    def set_histogram_data(self, data: Optional[Dict[str, np.ndarray]]) -> None:
        """Actualiza los datos del histograma y solicita repintado."""
        self._data = data
        self.update()

    def _on_toggled(self) -> None:
        self._show_r = self._cb_r.isChecked()
        self._show_g = self._cb_g.isChecked()
        self._show_b = self._cb_b.isChecked()
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        top_offset = 24.0
        plot_h = h - top_offset - 6.0

        # Fondo Liquid Glass oscuro
        bg_rect = QRectF(4.0, top_offset, w - 8.0, plot_h)
        painter.setPen(QPen(QColor(186, 230, 253, 70), 1))
        painter.setBrush(QBrush(QColor(7, 19, 34, 180)))
        painter.drawRoundedRect(bg_rect, 6.0, 6.0)

        if not self._data:
            return

        # Calcular valor maximo para normalizar verticalmente
        max_val = 1
        for key in ("r", "g", "b", "lum"):
            if key in self._data and len(self._data[key]) > 0:
                # Omitir picos extremos en 0 y 255 si distorsionan la escala
                trimmed = self._data[key][1:255] if len(self._data[key]) > 2 else self._data[key]
                if len(trimmed) > 0:
                    m = int(np.max(trimmed))
                    if m > max_val:
                        max_val = m

        if max_val <= 0:
            max_val = 1

        draw_w = bg_rect.width()
        draw_h = bg_rect.height() - 4.0
        base_y = bg_rect.bottom() - 2.0
        start_x = bg_rect.left()

        def draw_curve(values: np.ndarray, line_color: QColor, fill_color: QColor):
            path = QPainterPath()
            path.moveTo(start_x, base_y)

            for i in range(256):
                x = start_x + (i / 255.0) * draw_w
                val = float(values[i])
                y = base_y - min(draw_h, (val / float(max_val)) * draw_h)
                path.lineTo(x, y)

            path.lineTo(start_x + draw_w, base_y)
            path.closeSubpath()

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(fill_color))
            painter.drawPath(path)

            # Dibujar borde superior de la curva
            top_line = QPainterPath()
            for i in range(256):
                x = start_x + (i / 255.0) * draw_w
                val = float(values[i])
                y = base_y - min(draw_h, (val / float(max_val)) * draw_h)
                if i == 0:
                    top_line.moveTo(x, y)
                else:
                    top_line.lineTo(x, y)

            painter.setPen(QPen(line_color, 1.2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(top_line)

        # Dibujar curvas en orden B, G, R para mezcla
        if self._show_b and "b" in self._data:
            draw_curve(self._data["b"], QColor(56, 189, 248), QColor(2, 132, 199, 45))
        if self._show_g and "g" in self._data:
            draw_curve(self._data["g"], QColor(16, 185, 129), QColor(5, 150, 105, 45))
        if self._show_r and "r" in self._data:
            draw_curve(self._data["r"], QColor(239, 68, 68), QColor(220, 38, 38, 45))
