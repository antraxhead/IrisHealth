"""
Ventana principal de la aplicacion IrisHealth BioImaging.
Integra una experiencia clinica profesional con:
- Estetica Liquid Glass (Vidrio Liquido / Frosted Glass) en Modo Claro y Oscuro.
- Explorador microscopico con zoom interactivo, paneo, sonda de pixeles y regla caliper.
- Estacion de filtros morfologicos, ajuste de luminancia, control de fases espectrales y LUT.
- Histograma espectral en tiempo real para analisis cuantitativo.
- Descomposicion multicanal RGB simultanea.
- Cero strings hardcodeadas, cero rutas hardcodeadas y estricto cumplimiento sin emojis.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from PIL import Image

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabBar,
    QStackedWidget,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QComboBox,
    QGroupBox,
    QFileDialog,
    QMessageBox,
    QStatusBar,
    QSplitter,
    QFrame,
    QRadioButton,
    QButtonGroup,
)

from app.constants.strings import STRINGS
from app.constants.paths import (
    get_logo_path,
    get_samples_dir,
    get_theme_dark_icon_path,
    get_theme_light_icon_path,
)
from app.core.bioimage_reader import BioImageReader, BioImageItem, BioImageLoadError
from app.core.image_processor import ImageProcessor
from app.samples.sample_generator import SampleBioImageGenerator
from app.ui.components.image_canvas import ImageCanvas
from app.ui.components.channel_grid import ChannelGrid
from app.ui.components.report_dialog import ReportDialog
from app.ui.components.filter_panel import FilterPanel
from app.ui.styles import ThemeMode, get_stylesheet


class MainWindow(QMainWindow):
    """Ventana principal de la aplicacion de analisis y procesamiento de bioimagenes."""

    def __init__(self):
        super().__init__()
        self._bioimages: List[BioImageItem] = []
        self._current_index: int = -1
        self._current_theme: ThemeMode = ThemeMode.LIGHT

        # Arreglos de imagen para exploracion
        self._current_raw_array: Optional[Any] = None
        self._current_processed_array: Optional[Any] = None

        self.setWindowTitle(STRINGS.APP_WINDOW_TITLE)
        self.resize(1280, 840)
        self.setMinimumSize(1000, 680)

        # Configurar icono institucional dinamicamente
        logo_path = get_logo_path()
        if logo_path.exists():
            self.setWindowIcon(QIcon(str(logo_path)))

        self._setup_ui()
        self._setup_status_bar()
        self._apply_theme(ThemeMode.LIGHT)

        # Cargar automaticamente las bioimagenes de muestra de referencia
        self._load_sample_images_silently()

    def _setup_ui(self) -> None:
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ---------------------------------------------------------------------
        # BARRA 1: Cabecera Institucional y Acciones de Archivo (Ultra-compacta)
        # ---------------------------------------------------------------------
        header_frame = QFrame(self)
        header_frame.setObjectName("header_bar")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(12, 4, 12, 4)
        header_layout.setSpacing(8)

        # Logotipo institucional
        logo_path = get_logo_path()
        if logo_path.exists():
            lbl_logo = QLabel(header_frame)
            pix = QPixmap(str(logo_path)).scaled(
                26, 26,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            lbl_logo.setPixmap(pix)
            header_layout.addWidget(lbl_logo)

        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(0)
        lbl_brand_title = QLabel(STRINGS.APP_BRAND_TITLE, header_frame)
        lbl_brand_title.setObjectName("header_brand_title")
        lbl_brand_subtitle = QLabel(STRINGS.APP_BRAND_SUBTITLE, header_frame)
        lbl_brand_subtitle.setObjectName("header_brand_subtitle")
        brand_layout.addWidget(lbl_brand_title)
        brand_layout.addWidget(lbl_brand_subtitle)
        header_layout.addLayout(brand_layout)

        # Separador visual vertical
        sep1 = QFrame(header_frame)
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet("color: rgba(56, 189, 248, 0.35); max-width: 1px; margin: 4px 6px;")
        header_layout.addWidget(sep1)

        # Herramientas de Carga y Espacio (Integradas en Barra 1)
        self._btn_load = QPushButton(STRINGS.BTN_LOAD_IMAGE, header_frame)
        self._btn_load.clicked.connect(self._on_load_image)

        self._btn_load_folder = QPushButton(STRINGS.BTN_LOAD_FOLDER, header_frame)
        self._btn_load_folder.setObjectName("btn_secondary")
        self._btn_load_folder.clicked.connect(self._on_load_folder)

        self._btn_samples = QPushButton(STRINGS.BTN_LOAD_SAMPLES, header_frame)
        self._btn_samples.setObjectName("btn_secondary")
        self._btn_samples.clicked.connect(self._on_load_samples_clicked)

        self._btn_clear = QPushButton(STRINGS.BTN_CLEAR_ALL, header_frame)
        self._btn_clear.setObjectName("btn_secondary")
        self._btn_clear.clicked.connect(self._on_clear_all)

        header_layout.addWidget(self._btn_load)
        header_layout.addWidget(self._btn_load_folder)
        header_layout.addWidget(self._btn_samples)
        header_layout.addWidget(self._btn_clear)

        header_layout.addStretch()

        # Conmutador de tema Claro / Oscuro con SVG original
        self._btn_theme_toggle = QPushButton(header_frame)
        self._btn_theme_toggle.setObjectName("btn_secondary")
        self._btn_theme_toggle.clicked.connect(self._on_toggle_theme)
        self._btn_theme_toggle.setIconSize(QSize(16, 16))
        self._update_theme_button_ui()
        header_layout.addWidget(self._btn_theme_toggle)

        # Boton de emision de informe PDF en cabecera
        self._btn_export_pdf = QPushButton(STRINGS.BTN_EXPORT_PDF, header_frame)
        self._btn_export_pdf.setObjectName("btn_accent")
        self._btn_export_pdf.clicked.connect(self._on_open_report_dialog)
        header_layout.addWidget(self._btn_export_pdf)

        root_layout.addWidget(header_frame)

        # Linea de acento espectral ultrafina (2px)
        spectrum_bar = QFrame(self)
        spectrum_bar.setObjectName("spectrum_bar")
        root_layout.addWidget(spectrum_bar)

        # ---------------------------------------------------------------------
        # BARRA 2: Navegacion Integrada y Herramientas Clinicas (36px)
        # ---------------------------------------------------------------------
        secondary_frame = QFrame(self)
        secondary_frame.setObjectName("secondary_bar")
        secondary_layout = QHBoxLayout(secondary_frame)
        secondary_layout.setContentsMargins(10, 2, 10, 2)
        secondary_layout.setSpacing(8)

        # Pestanas de navegacion en Barra 2
        self._tab_bar = QTabBar(secondary_frame)
        self._tab_bar.setDrawBase(False)
        self._tab_bar.setUsesScrollButtons(False)
        self._tab_bar.setElideMode(Qt.TextElideMode.ElideNone)
        self._tab_bar.addTab(STRINGS.TAB_EXPLORER)
        self._tab_bar.addTab(STRINGS.TAB_MULTICHANNEL)
        self._tab_bar.currentChanged.connect(self._on_tab_changed)
        secondary_layout.addWidget(self._tab_bar)

        secondary_layout.addStretch()

        # Herramientas clinicas y de visualizacion
        self._btn_tool_pan = QPushButton(STRINGS.TOOL_PAN, secondary_frame)
        self._btn_tool_pan.setObjectName("btn_tool")
        self._btn_tool_pan.setCheckable(True)
        self._btn_tool_pan.setChecked(True)
        self._btn_tool_pan.clicked.connect(lambda: self._set_active_tool("pan"))

        self._btn_tool_measure = QPushButton(STRINGS.TOOL_MEASURE, secondary_frame)
        self._btn_tool_measure.setObjectName("btn_tool")
        self._btn_tool_measure.setCheckable(True)
        self._btn_tool_measure.setChecked(False)
        self._btn_tool_measure.clicked.connect(lambda: self._set_active_tool("measure"))

        self._btn_toggle_filters = QPushButton(STRINGS.TOOL_TOGGLE_PANEL, secondary_frame)
        self._btn_toggle_filters.setObjectName("btn_tool")
        self._btn_toggle_filters.setCheckable(True)
        self._btn_toggle_filters.setChecked(True)
        self._btn_toggle_filters.clicked.connect(self._on_toggle_filter_panel)

        secondary_layout.addWidget(self._btn_tool_pan)
        secondary_layout.addWidget(self._btn_tool_measure)
        secondary_layout.addWidget(self._btn_toggle_filters)

        root_layout.addWidget(secondary_frame)

        # ---------------------------------------------------------------------
        # ESPACIO DE TRABAJO PRINCIPAL: QStackedWidget de Maxima Visibilidad
        # ---------------------------------------------------------------------
        self._stack = QStackedWidget(central_widget)
        self._tab_explorer = self._build_explorer_tab()
        self._tab_multichannel = self._build_multichannel_tab()
        self._stack.addWidget(self._tab_explorer)
        self._stack.addWidget(self._tab_multichannel)

        root_layout.addWidget(self._stack, stretch=1)

    def _build_explorer_tab(self) -> QWidget:
        """Construye el explorador con visor ampliado y estacion de filtros retráctil."""
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal, widget)
        splitter.setObjectName("explorer_splitter")

        # 1. Panel Lateral Izquierdo: Serie y Metadatos de Adquisicion
        left_panel = QWidget(splitter)
        left_panel.setMinimumWidth(180)
        left_panel.setMaximumWidth(280)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 6, 0)
        left_layout.setSpacing(6)

        self._lbl_count = QLabel(STRINGS.EXPLORER_COUNT_LABEL.format(count=0), left_panel)
        self._lbl_count.setStyleSheet("font-weight: bold;")

        self._lbl_badge = QLabel(STRINGS.EXPLORER_SERIES_INSUFFICIENT.format(count=0), left_panel)
        self._lbl_badge.setObjectName("badge_warning")

        self._list_images = QListWidget(left_panel)
        self._list_images.currentRowChanged.connect(self._on_image_selected_from_list)

        self._group_meta = QGroupBox(STRINGS.EXPLORER_IMAGE_DETAILS_TITLE, left_panel)
        meta_layout = QVBoxLayout(self._group_meta)
        self._lbl_metadata = QLabel(STRINGS.EXPLORER_NO_SELECTION, self._group_meta)
        self._lbl_metadata.setWordWrap(True)
        self._lbl_metadata.setStyleSheet("font-size: 11px;")
        meta_layout.addWidget(self._lbl_metadata)

        left_layout.addWidget(self._lbl_count)
        left_layout.addWidget(self._lbl_badge)
        left_layout.addWidget(self._list_images, stretch=1)
        left_layout.addWidget(self._group_meta)

        # 2. Panel Central: Visor de Alta Resolucion Interactivo (FOCO PRINCIPAL)
        center_panel = QWidget(splitter)
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(4, 0, 4, 0)
        center_layout.setSpacing(0)

        self._canvas_preview = ImageCanvas(
            title=STRINGS.EXPLORER_PREVIEW_TITLE,
            interactive=True,
            parent=center_panel
        )
        center_layout.addWidget(self._canvas_preview, stretch=1)

        # 3. Panel Lateral Derecho: Estacion de Filtros, Fases y Rango Dinamico
        right_panel = QWidget(splitter)
        right_panel.setMinimumWidth(240)
        right_panel.setMaximumWidth(320)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(6, 0, 0, 0)
        right_layout.setSpacing(6)

        self._filter_panel = FilterPanel(parent=right_panel)
        self._filter_panel.pipeline_changed.connect(self._on_filter_pipeline_changed)
        self._filter_panel.reset_requested.connect(self._on_reset_filters)
        self._filter_panel.export_requested.connect(self._on_export_processed_image)
        right_layout.addWidget(self._filter_panel)

        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.addWidget(right_panel)

        # Asignar todo el crecimiento dinamico al visor central de la bioimagen
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([220, 780, 270])

        layout.addWidget(splitter, stretch=1)
        return widget

    def _build_multichannel_tab(self) -> QWidget:
        """Construye la estacion de descomposicion espectral y multicanal RGB maximizada."""
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # Barra de controles multicanal ultra-compacta (unifica selector, modo y herramientas)
        toolbar_frame = QFrame(widget)
        toolbar_frame.setObjectName("multichannel_toolbar")
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(8, 2, 8, 2)
        toolbar_layout.setSpacing(8)

        # 1. Selector de bioimagen
        lbl_select = QLabel(STRINGS.MULTICHANNEL_SELECT_IMAGE_LABEL, toolbar_frame)
        lbl_select.setStyleSheet("font-weight: 600; font-size: 11px;")

        self._combo_multichannel = QComboBox(toolbar_frame)
        self._combo_multichannel.setMinimumWidth(260)
        self._combo_multichannel.setMaximumWidth(360)
        self._combo_multichannel.currentIndexChanged.connect(self._on_multichannel_image_selected)

        toolbar_layout.addWidget(lbl_select)
        toolbar_layout.addWidget(self._combo_multichannel)

        # Separador vertical Liquid Glass
        sep_tool = QFrame(toolbar_frame)
        sep_tool.setFrameShape(QFrame.Shape.VLine)
        sep_tool.setStyleSheet("color: rgba(56, 189, 248, 0.35); max-width: 1px; margin: 3px 6px;")
        toolbar_layout.addWidget(sep_tool)

        # 2. Modo de presentacion espectral
        lbl_mode = QLabel(STRINGS.MULTICHANNEL_DISPLAY_MODE_LABEL, toolbar_frame)
        lbl_mode.setStyleSheet("font-weight: 600; font-size: 11px;")
        toolbar_layout.addWidget(lbl_mode)

        self._channel_grid = ChannelGrid(parent=widget)

        self._radio_color = QRadioButton(STRINGS.MULTICHANNEL_MODE_COLOR, toolbar_frame)
        self._radio_color.setChecked(False)
        self._radio_gray = QRadioButton(STRINGS.MULTICHANNEL_MODE_GRAYSCALE, toolbar_frame)
        self._radio_gray.setChecked(True)

        self._mode_group = QButtonGroup(toolbar_frame)
        self._mode_group.addButton(self._radio_gray, 0)
        self._mode_group.addButton(self._radio_color, 1)
        self._mode_group.idToggled.connect(self._channel_grid.on_mode_toggled)

        toolbar_layout.addWidget(self._radio_color)
        toolbar_layout.addWidget(self._radio_gray)

        # 3. Disposicion de visualizacion (Cuadricula 2x2 vs Tira Horizontal 1x4 estilo Color Separation)
        sep_layout = QFrame(toolbar_frame)
        sep_layout.setFrameShape(QFrame.Shape.VLine)
        sep_layout.setStyleSheet("color: rgba(56, 189, 248, 0.35); max-width: 1px; margin: 3px 6px;")
        toolbar_layout.addWidget(sep_layout)

        lbl_layout = QLabel(STRINGS.MULTICHANNEL_LAYOUT_LABEL, toolbar_frame)
        lbl_layout.setStyleSheet("font-weight: 600; font-size: 11px;")
        toolbar_layout.addWidget(lbl_layout)

        self._btn_layout_2x2 = QPushButton(STRINGS.MULTICHANNEL_LAYOUT_2X2, toolbar_frame)
        self._btn_layout_2x2.setObjectName("btn_layout_mode")
        self._btn_layout_2x2.setCheckable(True)
        self._btn_layout_2x2.setChecked(True)

        self._btn_layout_1x4 = QPushButton(STRINGS.MULTICHANNEL_LAYOUT_1X4, toolbar_frame)
        self._btn_layout_1x4.setObjectName("btn_layout_mode")
        self._btn_layout_1x4.setCheckable(True)
        self._btn_layout_1x4.setChecked(False)

        self._layout_group = QButtonGroup(toolbar_frame)
        self._layout_group.addButton(self._btn_layout_2x2, 0)
        self._layout_group.addButton(self._btn_layout_1x4, 1)
        self._layout_group.idClicked.connect(lambda bid: self._channel_grid.set_layout_mode("2x2" if bid == 0 else "1x4"))

        toolbar_layout.addWidget(self._btn_layout_2x2)
        toolbar_layout.addWidget(self._btn_layout_1x4)

        toolbar_layout.addStretch()

        # 4. Herramienta de centrado y ajuste simultaneo
        btn_fit_all = QPushButton(STRINGS.MULTICHANNEL_BTN_FIT_ALL, toolbar_frame)
        btn_fit_all.setObjectName("btn_secondary")
        btn_fit_all.setToolTip(STRINGS.MULTICHANNEL_TOOLTIP_FIT_ALL)
        btn_fit_all.clicked.connect(self._channel_grid.fit_all_canvases)
        toolbar_layout.addWidget(btn_fit_all)

        layout.addWidget(toolbar_frame)

        # Cuadricula 2x2 para canales RGB maximizada
        layout.addWidget(self._channel_grid, stretch=1)

        return widget

    def _setup_status_bar(self) -> None:
        self._status_bar = QStatusBar(self)
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage(STRINGS.APP_STATUS_READY)

    def _set_active_tool(self, mode: str) -> None:
        """Cambia la herramienta de exploracion activa y actualiza botones."""
        self._canvas_preview.set_tool_mode(mode)
        if mode == "pan":
            self._btn_tool_pan.setChecked(True)
            self._btn_tool_measure.setChecked(False)
            self._status_bar.showMessage("Herramienta activa: Paneo de exploracion libre.", 3000)
        elif mode == "measure":
            self._btn_tool_pan.setChecked(False)
            self._btn_tool_measure.setChecked(True)
            self._status_bar.showMessage("Herramienta activa: Regla de Caliper. Arrastre para medir.", 3000)

    def _on_toggle_filter_panel(self) -> None:
        """Muestra u oculta el panel lateral de filtros para otorgar maxima superficie a la bioimagen."""
        is_visible = self._filter_panel.isVisible()
        self._filter_panel.setVisible(not is_visible)
        self._btn_toggle_filters.setChecked(not is_visible)
        if not is_visible:
            self._status_bar.showMessage("Panel de filtros visible.", 3000)
        else:
            self._status_bar.showMessage("Panel de filtros minimizado para maxima visibilidad de bioimagen.", 3000)

    def _on_toggle_theme(self) -> None:
        """Alterna dinamicamente entre Modo Claro y Modo Oscuro Glacial."""
        if self._current_theme == ThemeMode.LIGHT:
            self._apply_theme(ThemeMode.DARK)
        else:
            self._apply_theme(ThemeMode.LIGHT)

    def _apply_theme(self, theme: ThemeMode) -> None:
        """Aplica la hoja de estilos globalmente a la aplicacion."""
        self._current_theme = theme
        sheet = get_stylesheet(theme)
        app = QApplication.instance()
        if app:
            app.setStyleSheet(sheet)
        else:
            self.setStyleSheet(sheet)
        self._update_theme_button_ui()

    def _update_theme_button_ui(self) -> None:
        """Actualiza el texto, icono SVG y tooltip del boton de tema."""
        if self._current_theme == ThemeMode.LIGHT:
            icon_path = get_theme_dark_icon_path()
            if icon_path.exists():
                self._btn_theme_toggle.setIcon(QIcon(str(icon_path)))
            self._btn_theme_toggle.setText(STRINGS.BTN_THEME_DARK)
            self._btn_theme_toggle.setToolTip(STRINGS.TOOLTIP_THEME_DARK)
        else:
            icon_path = get_theme_light_icon_path()
            if icon_path.exists():
                self._btn_theme_toggle.setIcon(QIcon(str(icon_path)))
            self._btn_theme_toggle.setText(STRINGS.BTN_THEME_LIGHT)
            self._btn_theme_toggle.setToolTip(STRINGS.TOOLTIP_THEME_LIGHT)

    def _load_sample_images_silently(self) -> None:
        """Genera y carga inicialmente las bioimagenes de muestra calibradas."""
        try:
            samples_dir = get_samples_dir()
            paths = SampleBioImageGenerator.ensure_sample_images_exist(samples_dir)
            for p in paths:
                item = BioImageReader.load_from_file(p)
                self._add_bioimage_item(item)
            self._update_all_views()
            self._status_bar.showMessage(STRINGS.MSG_SAMPLES_LOADED, 4000)
        except Exception:
            pass

    def _on_load_image(self) -> None:
        """Manejador para importar una bioimagen individual."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            STRINGS.FILE_DIALOG_OPEN_IMAGE,
            "",
            STRINGS.FILE_FILTER_BIOIMAGES,
        )
        if filepath:
            try:
                if filepath.lower().endswith(".zip"):
                    items = BioImageReader.load_from_zip(filepath)
                    for item in items:
                        self._add_bioimage_item(item)
                    self._status_bar.showMessage(f"Cargadas {len(items)} bioimagenes desde ZIP", 4000)
                else:
                    item = BioImageReader.load_from_file(filepath)
                    self._add_bioimage_item(item)
                    self._status_bar.showMessage(f"Bioimagen incorporada: {item.metadata.filename}", 4000)
                
                new_idx = len(self._bioimages) - 1
                self._update_all_views(select_index=new_idx)
            except BioImageLoadError as err:
                QMessageBox.critical(self, STRINGS.ERR_TITLE, str(err))

    def _on_load_folder(self) -> None:
        """Manejador para importar un directorio de serie de bioimagenes."""
        folder = QFileDialog.getExistingDirectory(self, STRINGS.FILE_DIALOG_OPEN_FOLDER, "")
        if folder:
            path_obj = Path(folder)
            added_count = 0
            for ext in BioImageReader.SUPPORTED_EXTENSIONS:
                for fpath in path_obj.glob(f"*{ext}"):
                    try:
                        if fpath.suffix.lower() == ".zip":
                            items = BioImageReader.load_from_zip(fpath)
                            for item in items:
                                self._add_bioimage_item(item)
                                added_count += 1
                        else:
                            item = BioImageReader.load_from_file(fpath)
                            self._add_bioimage_item(item)
                            added_count += 1
                    except Exception:
                        continue
            if added_count > 0:
                new_idx = len(self._bioimages) - 1
                self._update_all_views(select_index=new_idx)
                self._status_bar.showMessage(f"Se incorporaron {added_count} bioimagenes a la serie.", 4000)
            else:
                QMessageBox.information(
                    self,
                    STRINGS.INFO_TITLE,
                    "No se encontraron bioimagenes compatibles en el directorio seleccionado."
                )

    def _on_load_samples_clicked(self) -> None:
        """Recarga forzada de la serie de referencia calibrada."""
        self._load_sample_images_silently()
        QMessageBox.information(self, STRINGS.INFO_TITLE, STRINGS.MSG_SAMPLES_LOADED)

    def _on_clear_all(self) -> None:
        """Limpia todas las bioimagenes del espacio de trabajo."""
        self._bioimages.clear()
        self._current_index = -1
        self._current_raw_array = None
        self._current_processed_array = None
        self._list_images.clear()
        self._combo_multichannel.clear()
        self._canvas_preview.clear()
        self._channel_grid.clear()
        self._filter_panel.update_histogram(None)
        self._lbl_metadata.setText(STRINGS.EXPLORER_NO_SELECTION)
        self._update_badges()
        self._status_bar.showMessage(STRINGS.APP_STATUS_READY)

    def _add_bioimage_item(self, item: BioImageItem) -> None:
        """Agrega un elemento evitando duplicados por ruta de archivo."""
        for existing in self._bioimages:
            if existing.metadata.filepath == item.metadata.filepath:
                return
        self._bioimages.append(item)

    def _update_all_views(self, select_index: Optional[int] = None) -> None:
        """Sincroniza los controles de la interfaz con la serie actual de bioimagenes."""
        if select_index is not None and 0 <= select_index < len(self._bioimages):
            target_idx = select_index
        elif 0 <= self._current_index < len(self._bioimages):
            target_idx = self._current_index
        elif self._bioimages:
            target_idx = 0
        else:
            target_idx = -1

        self._list_images.blockSignals(True)
        self._list_images.clear()
        for item in self._bioimages:
            label_text = f"{item.metadata.filename} ({item.metadata.width}x{item.metadata.height})"
            self._list_images.addItem(QListWidgetItem(label_text))

        if 0 <= target_idx < len(self._bioimages):
            self._list_images.setCurrentRow(target_idx)
        self._list_images.blockSignals(False)

        # Actualizar combo de descomposicion multicanal
        self._combo_multichannel.blockSignals(True)
        self._combo_multichannel.clear()
        for item in self._bioimages:
            color_suffix = " (Color RGB)" if item.metadata.is_color else " (Monocromatico)"
            self._combo_multichannel.addItem(f"{item.metadata.filename}{color_suffix}", item)

        if 0 <= target_idx < len(self._bioimages):
            self._combo_multichannel.setCurrentIndex(target_idx)
        self._combo_multichannel.blockSignals(False)

        if 0 <= target_idx < len(self._bioimages):
            self._current_index = target_idx
            self._on_image_selected_from_list(target_idx)
            self._on_multichannel_image_selected(target_idx)

        self._update_badges()

    def _update_badges(self) -> None:
        """Actualiza el contador y la etiqueta de estado de la serie."""
        count = len(self._bioimages)
        self._lbl_count.setText(STRINGS.EXPLORER_COUNT_LABEL.format(count=count))
        if count >= 3:
            self._lbl_badge.setText(STRINGS.EXPLORER_SERIES_SUFFICIENT)
            self._lbl_badge.setObjectName("badge_success")
        else:
            self._lbl_badge.setText(STRINGS.EXPLORER_SERIES_INSUFFICIENT.format(count=count))
            self._lbl_badge.setObjectName("badge_warning")
        self._lbl_badge.style().unpolish(self._lbl_badge)
        self._lbl_badge.style().polish(self._lbl_badge)

    def _on_image_selected_from_list(self, row: int) -> None:
        """Manejador de seleccion de bioimagen en la lista del explorador."""
        if 0 <= row < len(self._bioimages):
            self._current_index = row
            item = self._bioimages[row]
            self._current_raw_array = item.original_array
            self._canvas_preview.set_title(item.metadata.filename)
            self._lbl_metadata.setText(item.metadata.formatted_summary())

            # Sincronizar combo multicanal con la imagen activa
            if self._combo_multichannel.currentIndex() != row:
                self._combo_multichannel.blockSignals(True)
                self._combo_multichannel.setCurrentIndex(row)
                self._combo_multichannel.blockSignals(False)
            self._channel_grid.load_bioimage(item)

            # Aplicar pipeline de filtros actual a la nueva imagen
            self._recalculate_pipeline()
        else:
            self._current_raw_array = None
            self._current_processed_array = None
            self._canvas_preview.clear()
            self._channel_grid.clear()
            self._filter_panel.update_histogram(None)
            self._lbl_metadata.setText(STRINGS.EXPLORER_NO_SELECTION)

    def _on_filter_pipeline_changed(self, params: Dict[str, Any]) -> None:
        """Re-procesa la bioimagen actual cuando cambia cualquier parametro del panel."""
        self._recalculate_pipeline(params)

    def _recalculate_pipeline(self, params: Optional[Dict[str, Any]] = None) -> None:
        """Aplica el pipeline vectorizado y actualiza el lienzo e histograma."""
        if self._current_raw_array is None:
            return

        if params is None:
            params = self._filter_panel.get_pipeline_params()

        self._current_processed_array = ImageProcessor.apply_pipeline(
            self._current_raw_array,
            brightness=params["brightness"],
            contrast=params["contrast"],
            gamma=params["gamma"],
            phase_red=params["phase_red"],
            phase_green=params["phase_green"],
            phase_blue=params["phase_blue"],
            spatial_filter=params["spatial_filter"],
            lut_mode=params["lut_mode"],
        )

        self._canvas_preview.set_numpy_array(self._current_processed_array)

        # Actualizar histograma en tiempo real
        hist_data = ImageProcessor.calculate_histogram(self._current_processed_array)
        self._filter_panel.update_histogram(hist_data)

    def _on_reset_filters(self) -> None:
        """Restaura la bioimagen a su estado natural."""
        self._recalculate_pipeline()
        self._status_bar.showMessage("Filtros restablecidos a valores originales.", 3000)

    def _on_export_processed_image(self) -> None:
        """Exporta la imagen procesada actual a disco."""
        if self._current_processed_array is None:
            QMessageBox.warning(self, STRINGS.WARN_TITLE, STRINGS.ERR_NO_IMAGES_LOADED)
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            STRINGS.DIALOG_SAVE_PROCESSED,
            "bioimagen_procesada.png",
            STRINGS.FILE_FILTER_EXPORT_IMAGE,
        )
        if save_path:
            try:
                img = Image.fromarray(self._current_processed_array)
                img.save(save_path)
                QMessageBox.information(
                    self,
                    STRINGS.INFO_TITLE,
                    STRINGS.MSG_IMAGE_EXPORTED.format(filepath=save_path)
                )
            except Exception as ex:
                QMessageBox.critical(self, STRINGS.ERR_TITLE, str(ex))

    def _on_multichannel_image_selected(self, index: int) -> None:
        """Manejador de seleccion de bioimagen para descomposicion multicanal."""
        if 0 <= index < len(self._bioimages):
            self._current_index = index
            item = self._bioimages[index]
            self._channel_grid.load_bioimage(item)

            # Sincronizar lista del explorador si difiere
            if self._list_images.currentRow() != index:
                self._list_images.blockSignals(True)
                self._list_images.setCurrentRow(index)
                self._list_images.blockSignals(False)
                self._current_raw_array = item.original_array
                self._canvas_preview.set_title(item.metadata.filename)
                self._lbl_metadata.setText(item.metadata.formatted_summary())
                self._recalculate_pipeline()

            if item.metadata.is_color:
                self._status_bar.showMessage(
                    f"Canales RGB descompuestos para: {item.metadata.filename}", 4000
                )
            else:
                self._status_bar.showMessage(
                    f"Descomposicion monocromatica multicanal para: {item.metadata.filename}", 4000
                )
        else:
            self._channel_grid.clear()

    def _on_tab_changed(self, index: int) -> None:
        """Sincroniza las vistas al alternar entre explorador y descomposicion multicanal."""
        self._stack.setCurrentIndex(index)
        if index == 0:
            self._btn_tool_pan.setVisible(True)
            self._btn_tool_measure.setVisible(True)
            self._btn_toggle_filters.setVisible(True)
            self._btn_tool_pan.setEnabled(True)
            self._btn_tool_measure.setEnabled(True)
            self._btn_toggle_filters.setEnabled(True)
            if 0 <= self._current_index < len(self._bioimages):
                if self._list_images.currentRow() != self._current_index:
                    self._list_images.setCurrentRow(self._current_index)
        elif index == 1:
            self._btn_tool_pan.setVisible(False)
            self._btn_tool_measure.setVisible(False)
            self._btn_toggle_filters.setVisible(False)
            self._btn_tool_pan.setEnabled(False)
            self._btn_tool_measure.setEnabled(False)
            self._btn_toggle_filters.setEnabled(False)
            if 0 <= self._current_index < len(self._bioimages):
                if self._combo_multichannel.currentIndex() != self._current_index:
                    self._combo_multichannel.blockSignals(True)
                    self._combo_multichannel.setCurrentIndex(self._current_index)
                    self._combo_multichannel.blockSignals(False)
                self._channel_grid.load_bioimage(self._bioimages[self._current_index])

    @property
    def _tabs(self):
        """Propiedad de compatibilidad retroactiva para acceso a pestanas."""
        return self._tab_bar

    def _on_open_report_dialog(self) -> None:
        """Abre la ventana modal para configurar y emitir el informe clinico/academico en PDF."""
        if len(self._bioimages) < 3:
            QMessageBox.warning(
                self,
                STRINGS.WARN_TITLE,
                STRINGS.ERR_LESS_THAN_THREE_IMAGES.format(count=len(self._bioimages))
            )
            return

        dialog = ReportDialog(self._bioimages, self)
        dialog.exec()
