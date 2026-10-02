"""
Lienzo interactivo de exploracion clinica de bioimagenes con estetica Liquid Glass.
Implementa:
- Escalado y ajuste automatico (Fit) reactivo al tamano real de la ventana.
- Zoom continuo con rueda de raton centrado en el cursor (15% a 1200%).
- Paneo y navegacion bidireccional por arrastre.
- Sonda de pixeles en tiempo real (X, Y, R, G, B, Luminancia).
- Regla de medicion / Caliper digital para estructuras celulares.
- HUD flotante de vidrio translucido con informacion dinamica.
"""

from typing import Optional, Tuple
import numpy as np

from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtGui import (
    QPainter,
    QPixmap,
    QColor,
    QPen,
    QBrush,
    QFont,
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)

from app.constants.strings import STRINGS
from app.core.image_processor import ImageProcessor


class ImageCanvas(QWidget):
    """Visor interactivo con navegacion, sonda de pixeles y regla caliper."""

    pixel_probed = Signal(int, int, int, int, int)  # x, y, r, g, b
    measurement_changed = Signal(float)             # pixels

    def __init__(self, title: str = "", interactive: bool = True, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._title = title
        self._interactive = interactive

        self._raw_array: Optional[np.ndarray] = None
        self._rendered_pixmap: Optional[QPixmap] = None

        # Parametros de transformacion espacial y reactividad
        self._zoom: float = 1.0
        self._pan_offset: QPointF = QPointF(0.0, 0.0)
        self._last_mouse_pos: QPointF = QPointF(0.0, 0.0)
        self._is_panning: bool = False
        self._user_has_zoomed: bool = False

        # Herramientas
        self._tool_mode: str = "pan"  # "pan", "measure"
        self._measure_start: Optional[QPointF] = None
        self._measure_end: Optional[QPointF] = None
        self._current_probe_info: str = STRINGS.HUD_PROBE_IDLE
        self._auto_hud_probe: bool = True

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(3, 3, 3, 3)
        self._layout.setSpacing(2)

        # Barra superior compacta para lienzos interactivos
        if self._interactive:
            top_bar = QHBoxLayout()
            top_bar.setContentsMargins(3, 1, 3, 1)
            top_bar.setSpacing(4)

            self._title_label = QLabel(self._title, self)
            self._title_label.setStyleSheet("font-weight: bold; font-size: 11px; color: #E0F2FE; background: transparent;")
            top_bar.addWidget(self._title_label)
            top_bar.addStretch()

            self._btn_zoom_in = QPushButton("+", self)
            self._btn_zoom_in.setFixedSize(22, 19)
            self._btn_zoom_in.setObjectName("btn_canvas_tool")
            self._btn_zoom_in.setToolTip(STRINGS.TOOL_ZOOM_IN)
            self._btn_zoom_in.clicked.connect(lambda: self.zoom_by(1.25))

            self._btn_zoom_out = QPushButton("-", self)
            self._btn_zoom_out.setFixedSize(22, 19)
            self._btn_zoom_out.setObjectName("btn_canvas_tool")
            self._btn_zoom_out.setToolTip(STRINGS.TOOL_ZOOM_OUT)
            self._btn_zoom_out.clicked.connect(lambda: self.zoom_by(0.8))

            self._btn_zoom_fit = QPushButton("Fit", self)
            self._btn_zoom_fit.setFixedSize(32, 19)
            self._btn_zoom_fit.setObjectName("btn_canvas_tool")
            self._btn_zoom_fit.setToolTip(STRINGS.TOOL_ZOOM_FIT)
            self._btn_zoom_fit.clicked.connect(self.fit_to_window)

            self._btn_zoom_100 = QPushButton("1:1", self)
            self._btn_zoom_100.setFixedSize(32, 19)
            self._btn_zoom_100.setObjectName("btn_canvas_tool")
            self._btn_zoom_100.setToolTip(STRINGS.TOOL_ZOOM_100)
            self._btn_zoom_100.clicked.connect(self.reset_to_100)

            top_bar.addWidget(self._btn_zoom_in)
            top_bar.addWidget(self._btn_zoom_out)
            top_bar.addWidget(self._btn_zoom_fit)
            top_bar.addWidget(self._btn_zoom_100)

            self._layout.addLayout(top_bar)
        elif self._title:
            self._title_label = QLabel(self._title, self)
            self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._title_label.setStyleSheet("font-weight: bold; font-size: 11px; color: #E0F2FE; background: transparent;")
            self._layout.addWidget(self._title_label)
        else:
            self._title_label = None

        self._layout.addStretch(1)

        # HUD inferior translucido (Liquid Glass overlay)
        if self._interactive:
            self._hud_bar = QLabel(self._current_probe_info, self)
            self._hud_bar.setFixedHeight(20)
            self._hud_bar.setStyleSheet(
                "background-color: rgba(11, 27, 46, 210); border: 1px solid rgba(186, 230, 253, 0.4);"
                "border-radius: 3px; padding: 1px 6px; color: #7DD3FC; font-size: 10px; font-weight: 500;"
            )
            self._layout.addWidget(self._hud_bar)
        else:
            self._hud_bar = None

    def set_hud_text(self, text: str) -> None:
        """Actualiza el texto informativo del HUD inferior."""
        self._current_probe_info = text
        if self._hud_bar:
            self._hud_bar.setText(text)

    def set_auto_hud_probe(self, enabled: bool) -> None:
        """Habilita o deshabilita la actualizacion automatica por defecto del HUD de sonda."""
        self._auto_hud_probe = enabled

    def set_title(self, title: str) -> None:
        """Actualiza el titulo del lienzo."""
        self._title = title
        if self._title_label:
            self._title_label.setText(title)

    def set_numpy_array(self, array: Optional[np.ndarray]) -> None:
        """Carga y procesa un nuevo arreglo NumPy de imagen."""
        self._raw_array = array
        if array is None:
            self._rendered_pixmap = None
            self.update()
            return

        qimg = ImageProcessor.numpy_to_qimage(array)
        self._rendered_pixmap = QPixmap.fromImage(qimg)
        self._user_has_zoomed = False
        self.fit_to_window()

    def get_current_array(self) -> Optional[np.ndarray]:
        """Devuelve el arreglo matricial cargado actualmente."""
        return self._raw_array

    def clear(self) -> None:
        """Limpia el contenido del lienzo."""
        self._raw_array = None
        self._rendered_pixmap = None
        self._measure_start = None
        self._measure_end = None
        self._user_has_zoomed = False
        if self._hud_bar:
            self._hud_bar.setText(STRINGS.EXPLORER_NO_SELECTION)
        self.update()

    def set_tool_mode(self, mode: str) -> None:
        """Establece la herramienta activa ('pan', 'measure')."""
        self._tool_mode = mode
        if mode == "measure":
            self.setCursor(Qt.CursorShape.CrossCursor)
            if self._hud_bar:
                self._hud_bar.setText(STRINGS.HUD_MEASURE_HINT)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            if self._hud_bar:
                self._hud_bar.setText(STRINGS.HUD_PROBE_IDLE)
        self.update()

    def fit_to_window(self) -> None:
        """Calcula y aplica el factor de zoom optimo para llenar el visor disponible."""
        if self._rendered_pixmap is None or self._rendered_pixmap.isNull():
            return

        img_w = float(self._rendered_pixmap.width())
        img_h = float(self._rendered_pixmap.height())

        top_margin = 23.0 if self._interactive else 4.0
        bottom_margin = 22.0 if (self._interactive and self._hud_bar) else 4.0

        view_w = max(50.0, float(self.width()) - 8.0)
        view_h = max(50.0, float(self.height()) - top_margin - bottom_margin - 6.0)

        scale_x = view_w / img_w
        scale_y = view_h / img_h
        self._zoom = min(scale_x, scale_y)
        self._user_has_zoomed = False
        self._center_image()
        self.update()

    def reset_to_100(self) -> None:
        """Restaura la escala al 100% (1:1 pixeles de pantalla por pixel de imagen)."""
        self._zoom = 1.0
        self._user_has_zoomed = True
        self._center_image()
        self.update()

    def zoom_by(self, factor: float) -> None:
        """Modifica el zoom relativo manteniendo el centro relativo."""
        self._zoom = float(np.clip(self._zoom * factor, 0.15, 12.0))
        self._user_has_zoomed = True
        self.update()

    def _center_image(self) -> None:
        """Centra la imagen en el area disponible del lienzo."""
        if self._rendered_pixmap is None:
            return
        w = float(self.width())
        h = float(self.height())
        scaled_w = float(self._rendered_pixmap.width()) * self._zoom
        scaled_h = float(self._rendered_pixmap.height()) * self._zoom

        top_margin = 23.0 if self._interactive else 4.0
        bottom_margin = 22.0 if (self._interactive and self._hud_bar) else 4.0
        avail_h = h - top_margin - bottom_margin

        pos_x = (w - scaled_w) / 2.0
        pos_y = top_margin + (avail_h - scaled_h) / 2.0
        self._pan_offset = QPointF(pos_x, pos_y)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if not self._user_has_zoomed and self._rendered_pixmap:
            self.fit_to_window()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if not self._user_has_zoomed and self._rendered_pixmap:
            self.fit_to_window()

    # --- Eventos de Interaccion con Raton ---

    def wheelEvent(self, event) -> None:
        if not self._interactive or self._rendered_pixmap is None:
            return

        delta = event.angleDelta().y()
        factor = 1.2 if delta > 0 else 0.82
        old_zoom = self._zoom
        new_zoom = float(np.clip(old_zoom * factor, 0.15, 12.0))

        # Zoom centrado sobre la posicion del cursor
        mouse_pos = event.position()
        self._pan_offset = mouse_pos - (mouse_pos - self._pan_offset) * (new_zoom / old_zoom)
        self._zoom = new_zoom
        self._user_has_zoomed = True
        self.update()
        event.accept()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if self._tool_mode == "measure":
                self._measure_start = event.position()
                self._measure_end = event.position()
            else:
                self._is_panning = True
                self._last_mouse_pos = event.position()
                if self._interactive:
                    self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.update()

    def mouseMoveEvent(self, event) -> None:
        pos = event.position()

        if self._is_panning:
            delta = pos - self._last_mouse_pos
            self._pan_offset += delta
            self._last_mouse_pos = pos
            self._user_has_zoomed = True
            self.update()
        elif self._tool_mode == "measure" and self._measure_start is not None:
            self._measure_end = pos
            self._update_measurement_hud()
            self.update()

        self._update_probe_under_cursor(pos)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if self._is_panning:
                self._is_panning = False
                if self._interactive and self._tool_mode != "measure":
                    self.setCursor(Qt.CursorShape.ArrowCursor)
            elif self._tool_mode == "measure":
                self._measure_end = event.position()
                self._update_measurement_hud()
            self.update()

    def _image_coords_from_screen(self, screen_pos: QPointF) -> Optional[Tuple[int, int]]:
        """Convierte una coordenada de pantalla en coordenadas reales del pixel de bioimagen."""
        if self._rendered_pixmap is None or self._zoom <= 0:
            return None

        rel_x = (screen_pos.x() - self._pan_offset.x()) / self._zoom
        rel_y = (screen_pos.y() - self._pan_offset.y()) / self._zoom

        img_w = self._rendered_pixmap.width()
        img_h = self._rendered_pixmap.height()

        if 0 <= rel_x < img_w and 0 <= rel_y < img_h:
            return int(rel_x), int(rel_y)
        return None

    def _update_probe_under_cursor(self, screen_pos: QPointF) -> None:
        """Lee e informa los valores multicanal exactos del tejido bajo el cursor."""
        coords = self._image_coords_from_screen(screen_pos)
        if coords and self._raw_array is not None:
            x, y = coords
            h, w = self._raw_array.shape[:2]
            if 0 <= y < h and 0 <= x < w:
                if self._raw_array.ndim == 3 and self._raw_array.shape[2] >= 3:
                    r = int(self._raw_array[y, x, 0])
                    g = int(self._raw_array[y, x, 1])
                    b = int(self._raw_array[y, x, 2])
                    lum = int(0.299 * r + 0.587 * g + 0.114 * b)
                else:
                    val = int(self._raw_array[y, x]) if self._raw_array.ndim == 2 else int(self._raw_array[y, x, 0])
                    r, g, b, lum = val, val, val, val

                self.pixel_probed.emit(x, y, r, g, b)
                if self._auto_hud_probe and self._hud_bar and self._tool_mode != "measure":
                    self._hud_bar.setText(STRINGS.HUD_PROBE_TEXT.format(x=x, y=y, r=r, g=g, b=b, lum=lum))
                return

        if self._auto_hud_probe and self._hud_bar and self._tool_mode != "measure":
            self._hud_bar.setText(STRINGS.HUD_PROBE_IDLE)

    def _update_measurement_hud(self) -> None:
        """Calcula la distancia euclidiana en pixeles y estima micras."""
        if not self._measure_start or not self._measure_end or self._zoom <= 0:
            return

        dx = (self._measure_end.x() - self._measure_start.x()) / self._zoom
        dy = (self._measure_end.y() - self._measure_start.y()) / self._zoom
        pixel_dist = float(np.hypot(dx, dy))
        microns = pixel_dist * 0.45

        self.measurement_changed.emit(pixel_dist)
        if self._hud_bar:
            self._hud_bar.setText(STRINGS.HUD_MEASURE_TEXT.format(pixels=pixel_dist, microns=microns))

    # --- Renderizado Visual ---

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w = float(self.width())
        h = float(self.height())

        # Fondo del lienzo: Fosa glacial profunda con marco Liquid Glass
        bg_rect = QRectF(0, 0, w, h)
        painter.setPen(QPen(QColor(186, 230, 253, 50), 1))
        painter.setBrush(QBrush(QColor(7, 19, 34)))
        painter.drawRoundedRect(bg_rect, 6.0, 6.0)

        # Dibujar imagen escalada
        if self._rendered_pixmap and not self._rendered_pixmap.isNull():
            if not self._user_has_zoomed:
                img_w = float(self._rendered_pixmap.width())
                img_h = float(self._rendered_pixmap.height())
                top_margin = 23.0 if self._interactive else 4.0
                bottom_margin = 22.0 if (self._interactive and self._hud_bar) else 4.0
                view_w = max(50.0, w - 8.0)
                view_h = max(50.0, h - top_margin - bottom_margin - 6.0)
                if img_w > 0 and img_h > 0 and view_w > 50 and view_h > 50:
                    scale_x = view_w / img_w
                    scale_y = view_h / img_h
                    self._zoom = min(scale_x, scale_y)
                    avail_h = max(10.0, h - top_margin - bottom_margin)
                    scaled_w = img_w * self._zoom
                    scaled_h = img_h * self._zoom
                    pos_x = (w - scaled_w) / 2.0
                    pos_y = top_margin + (avail_h - scaled_h) / 2.0
                    self._pan_offset = QPointF(pos_x, pos_y)

            painter.save()
            painter.translate(self._pan_offset)
            painter.scale(self._zoom, self._zoom)
            painter.drawPixmap(0, 0, self._rendered_pixmap)
            painter.restore()

            # Dibujar Caliper
            if self._measure_start and self._measure_end and self._tool_mode == "measure":
                painter.setPen(QPen(QColor(56, 189, 248), 2, Qt.PenStyle.SolidLine))
                painter.drawLine(self._measure_start, self._measure_end)

                painter.setBrush(QBrush(QColor(240, 249, 255)))
                painter.drawEllipse(self._measure_start, 4, 4)
                painter.drawEllipse(self._measure_end, 4, 4)
        else:
            painter.setPen(QColor(125, 211, 252, 160))
            font = QFont("Segoe UI", 11)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(bg_rect, Qt.AlignmentFlag.AlignCenter, STRINGS.EXPLORER_NO_SELECTION)
