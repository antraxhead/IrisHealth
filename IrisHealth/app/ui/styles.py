"""
Modulo de estilos de IrisHealth con estetica Liquid Glass (Vidrio Liquido / Frosted Glass):
- Superficies translucidas con brillo refractivo y bordes de cristal.
- Modo Claro: Blanco escarcha semitransparente con tipografia de maximo contraste (#0C2340).
- Modo Oscuro: Vidrio obsidiana polar con iluminacion interior de neon cyan (#38BDF8).
- Diseno ultra-compacto de cabecera en maximo dos barras para maximizar el area visual.
"""

from enum import Enum


class ThemeMode(Enum):
    LIGHT = "light"
    DARK = "dark"


_LIGHT_STYLESHEET = """
QMainWindow, QDialog {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F4F9FD, stop:1 #EBF3FA);
    color: #0C2340;
}

/* Regla Universal de Etiquetas para Maximo Contraste */
QLabel {
    color: #0C2340;
}

QRadioButton {
    color: #0C2340;
    font-size: 11px;
    font-weight: 500;
    spacing: 5px;
}

/* Barra 1: Cabecera Principal Compacta (40px) */
QFrame#header_bar {
    background-color: rgba(10, 28, 48, 0.96);
    border-bottom: 1px solid #0284C7;
    min-height: 40px;
    max-height: 40px;
}

QLabel#header_brand_title {
    font-size: 16px;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: 0.5px;
}

QLabel#header_brand_subtitle {
    font-size: 11px;
    color: #7DD3FC;
    font-weight: 500;
}

/* Barra 2: Navegacion y Herramientas Clinicas (36px) */
QFrame#secondary_bar {
    background: rgba(255, 255, 255, 0.85);
    border-bottom: 1px solid rgba(186, 230, 253, 0.7);
    min-height: 36px;
    max-height: 36px;
}

/* Barra de Acento Glacial Ultrafina */
QFrame#spectrum_bar {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #0369A1,
        stop:0.25 #0284C7,
        stop:0.50 #0EA5E9,
        stop:0.75 #06B6D4,
        stop:1.0 #38BDF8
    );
    max-height: 2px;
    min-height: 2px;
    border: none;
}

/* Pestanas Liquid Glass Compactas */
QTabWidget::pane {
    border: 1px solid rgba(186, 230, 253, 0.7);
    background: rgba(255, 255, 255, 0.75);
    border-radius: 6px;
    top: -1px;
}

QTabBar {
    background: transparent;
    border: none;
}

QTabBar::tab {
    background: rgba(224, 242, 254, 0.6);
    color: #0369A1;
    padding: 5px 16px;
    border-radius: 4px;
    margin: 2px 3px;
    font-weight: 600;
    font-size: 11.5px;
    border: 1px solid rgba(186, 230, 253, 0.5);
}

QTabBar::tab:selected {
    background: rgba(255, 255, 255, 0.95);
    color: #0C4A6E;
    border: 1px solid #0284C7;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background: rgba(186, 230, 253, 0.75);
    color: #082F49;
}

/* Paneles y Tarjetas de Vidrio */
QGroupBox {
    font-weight: bold;
    border: 1px solid rgba(186, 230, 253, 0.75);
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 12px;
    background-color: rgba(255, 255, 255, 0.68);
    color: #0C4A6E;
    font-size: 11.5px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 6px;
    color: #0C4A6E;
    background: transparent;
}

QGroupBox QLabel {
    color: #0C2340;
    font-size: 11px;
}

/* Barra de Controles Multicanal Compacta */
QFrame#multichannel_toolbar {
    background-color: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(186, 230, 253, 0.8);
    border-radius: 6px;
    min-height: 32px;
    max-height: 32px;
}

/* Cinta Horizontal de Metricas Cuantitativas */
QFrame#stats_horizontal_panel {
    background-color: rgba(255, 255, 255, 0.75);
    border: 1px solid rgba(186, 230, 253, 0.8);
    border-radius: 6px;
    min-height: 36px;
    max-height: 40px;
}

QFrame#stats_card_red {
    background-color: rgba(254, 242, 242, 0.85);
    border: 1px solid rgba(252, 165, 165, 0.6);
    border-left: 3px solid #DC2626;
    border-radius: 4px;
}

QFrame#stats_card_green {
    background-color: rgba(240, 253, 244, 0.85);
    border: 1px solid rgba(134, 239, 172, 0.6);
    border-left: 3px solid #059669;
    border-radius: 4px;
}

QFrame#stats_card_blue {
    background-color: rgba(240, 249, 255, 0.85);
    border: 1px solid rgba(186, 230, 253, 0.7);
    border-left: 3px solid #0284C7;
    border-radius: 4px;
}

QLabel#stats_card_title_r {
    color: #B91C1C;
    font-weight: 700;
    font-size: 10.5px;
}

QLabel#stats_card_title_g {
    color: #047857;
    font-weight: 700;
    font-size: 10.5px;
}

QLabel#stats_card_title_b {
    color: #0369A1;
    font-weight: 700;
    font-size: 10.5px;
}

QLabel#stats_card_val {
    color: #1E293B;
    font-size: 10.5px;
    font-weight: 600;
}

/* Botones Liquid Glass */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0284C7, stop:1 #0369A1);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.35);
    border-radius: 5px;
    padding: 4px 11px;
    font-weight: 600;
    font-size: 11.5px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #38BDF8, stop:1 #0284C7);
}

QPushButton:pressed {
    background: #075985;
}

QPushButton:disabled {
    background-color: #CBD5E1;
    color: #94A3B8;
}

QPushButton#btn_secondary {
    background: rgba(224, 242, 254, 0.75);
    color: #0369A1;
    border: 1px solid rgba(186, 230, 253, 0.9);
}

QPushButton#btn_secondary:hover {
    background: rgba(186, 230, 253, 0.85);
    color: #082F49;
    border-color: #7DD3FC;
}

QPushButton#btn_secondary:pressed {
    background: #7DD3FC;
    color: #082F49;
}

QPushButton#btn_accent {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0891B2, stop:1 #0E7490);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.4);
}

QPushButton#btn_accent:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #06B6D4, stop:1 #0891B2);
}

QPushButton#btn_accent:pressed {
    background: #155E75;
}

QPushButton#btn_tool {
    background: rgba(224, 242, 254, 0.75);
    color: #0369A1;
    border: 1px solid rgba(186, 230, 253, 0.9);
    border-radius: 4px;
    padding: 3px 10px;
    font-weight: 600;
    font-size: 11px;
}

QPushButton#btn_tool:hover {
    background: rgba(186, 230, 253, 0.9);
    color: #0C4A6E;
    border-color: #0284C7;
}

QPushButton#btn_tool:checked {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0284C7, stop:1 #0369A1);
    color: #FFFFFF;
    border-color: #0369A1;
}

QPushButton#btn_canvas_tool {
    background: rgba(14, 29, 49, 0.85);
    color: #BAE6FD;
    border: 1px solid rgba(56, 189, 248, 0.4);
    border-radius: 3px;
    font-size: 11px;
    font-weight: bold;
    padding: 1px 4px;
}

QPushButton#btn_canvas_tool:hover {
    background: rgba(2, 132, 199, 0.9);
    color: #FFFFFF;
    border-color: #38BDF8;
}

QPushButton#btn_canvas_tool:pressed {
    background: #075985;
}

/* Listas con Translucidez */
QListWidget {
    background-color: rgba(255, 255, 255, 0.75);
    color: #0C2340;
    border: 1px solid rgba(186, 230, 253, 0.75);
    border-radius: 6px;
    padding: 3px;
    font-size: 11.5px;
}

QListWidget::item {
    padding: 5px 8px;
    border-radius: 4px;
    border-bottom: 1px solid rgba(240, 249, 255, 0.8);
    color: #0C2340;
}

QListWidget::item:selected {
    background-color: rgba(224, 242, 254, 0.9);
    color: #0284C7;
    font-weight: bold;
    border-left: 3px solid #0284C7;
}

QListWidget::item:hover:!selected {
    background-color: rgba(240, 249, 255, 0.6);
    color: #0369A1;
}

/* Controles de Entrada */
QComboBox {
    background-color: rgba(255, 255, 255, 0.9);
    color: #0C2340;
    border: 1px solid rgba(186, 230, 253, 0.85);
    border-radius: 5px;
    padding: 3px 8px;
    min-height: 20px;
    font-size: 11.5px;
}

QComboBox:hover, QComboBox:focus {
    border-color: #0284C7;
}

QComboBox::drop-down {
    border: none;
    width: 18px;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    color: #0C2340;
    selection-background-color: #E0F2FE;
    selection-color: #0284C7;
    border: 1px solid #BAE6FD;
}

QLineEdit {
    background-color: rgba(255, 255, 255, 0.9);
    color: #0C2340;
    border: 1px solid rgba(186, 230, 253, 0.85);
    border-radius: 5px;
    padding: 4px 6px;
    font-size: 11.5px;
}

QLineEdit:focus {
    border: 1px solid #0284C7;
    background-color: #F0F9FF;
}

/* Sliders Liquid Glass Compactos */
QSlider::groove:horizontal {
    height: 4px;
    background: rgba(186, 230, 253, 0.7);
    border-radius: 2px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #38BDF8);
    border-radius: 2px;
}

QSlider::handle:horizontal {
    width: 13px;
    height: 13px;
    margin: -4.5px 0;
    border-radius: 6.5px;
    background: #FFFFFF;
    border: 2px solid #0284C7;
}

QSlider::handle:horizontal:hover {
    background: #0284C7;
    border-color: #FFFFFF;
}

/* Barra de Estado Compacta */
QStatusBar {
    background-color: rgba(224, 242, 254, 0.7);
    border-top: 1px solid rgba(186, 230, 253, 0.7);
    color: #0369A1;
    font-size: 11px;
    font-weight: 500;
}

/* Badges */
QLabel#badge_success {
    background-color: rgba(224, 242, 254, 0.85);
    color: #0369A1;
    font-weight: bold;
    padding: 2px 7px;
    border-radius: 4px;
    border: 1px solid #7DD3FC;
    font-size: 10.5px;
}

QLabel#badge_warning {
    background-color: rgba(254, 243, 199, 0.85);
    color: #92400E;
    font-weight: bold;
    padding: 2px 7px;
    border-radius: 4px;
    border: 1px solid #FCD34D;
    font-size: 10.5px;
}

/* Badges de Separacion de Canales (Estilo Color Separation) */
QLabel#badge_channel_orig {
    background-color: rgba(71, 85, 105, 0.9);
    color: #FFFFFF;
    font-weight: bold;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid #334155;
    font-size: 11px;
}

QLabel#badge_channel_red {
    background-color: #DC2626;
    color: #FFFFFF;
    font-weight: bold;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid #B91C1C;
    font-size: 11px;
}

QLabel#badge_channel_green {
    background-color: #16A34A;
    color: #FFFFFF;
    font-weight: bold;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid #15803D;
    font-size: 11px;
}

QLabel#badge_channel_blue {
    background-color: #2563EB;
    color: #FFFFFF;
    font-weight: bold;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid #1D4ED8;
    font-size: 11px;
}

QPushButton#btn_layout_mode {
    background-color: rgba(224, 242, 254, 0.75);
    color: #0284C7;
    border: 1px solid #BAE6FD;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}

QPushButton#btn_layout_mode:checked {
    background-color: #0284C7;
    color: #FFFFFF;
    border: 1px solid #0369A1;
}
"""

_DARK_STYLESHEET = """
QMainWindow, QDialog {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #050B14, stop:1 #07101E);
    color: #F0F8FF;
}

/* Regla Universal de Etiquetas en Modo Oscuro */
QLabel {
    color: #F0F8FF;
}

QRadioButton {
    color: #F0F8FF;
    font-size: 11px;
    font-weight: 500;
    spacing: 5px;
}

/* Barra 1: Cabecera Principal Compacta (40px) */
QFrame#header_bar {
    background-color: rgba(3, 7, 14, 0.96);
    border-bottom: 1px solid #0EA5E9;
    min-height: 40px;
    max-height: 40px;
}

QLabel#header_brand_title {
    font-size: 16px;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: 0.5px;
}

QLabel#header_brand_subtitle {
    font-size: 11px;
    color: #7DD3FC;
    font-weight: 500;
}

/* Barra 2: Navegacion y Herramientas Clinicas (36px) */
QFrame#secondary_bar {
    background: rgba(11, 22, 38, 0.85);
    border-bottom: 1px solid rgba(56, 189, 248, 0.25);
    min-height: 36px;
    max-height: 36px;
}

/* Barra de Acento de Neon Glacial */
QFrame#spectrum_bar {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #0284C7,
        stop:0.30 #0EA5E9,
        stop:0.60 #38BDF8,
        stop:1.0 #67E8F9
    );
    max-height: 2px;
    min-height: 2px;
    border: none;
}

/* Pestanas Dark Liquid Glass Compactas */
QTabWidget::pane {
    border: 1px solid rgba(56, 189, 248, 0.25);
    background: rgba(11, 22, 38, 0.75);
    border-radius: 6px;
    top: -1px;
}

QTabBar {
    background: transparent;
    border: none;
}

QTabBar::tab {
    background: rgba(14, 29, 49, 0.65);
    color: #7DD3FC;
    padding: 5px 16px;
    border-radius: 4px;
    margin: 2px 3px;
    font-weight: 600;
    font-size: 11.5px;
    border: 1px solid rgba(56, 189, 248, 0.2);
}

QTabBar::tab:selected {
    background: rgba(21, 43, 71, 0.95);
    color: #FFFFFF;
    border: 1px solid #38BDF8;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background: rgba(30, 58, 95, 0.65);
    color: #BAE6FD;
}

/* Paneles y Tarjetas Dark Glass */
QGroupBox {
    font-weight: bold;
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 12px;
    background-color: rgba(11, 22, 38, 0.65);
    color: #38BDF8;
    font-size: 11.5px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 6px;
    color: #38BDF8;
    background: transparent;
}

QGroupBox QLabel {
    color: #BAE6FD;
    font-size: 11px;
}

/* Barra de Controles Multicanal Compacta */
QFrame#multichannel_toolbar {
    background-color: rgba(11, 22, 38, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 6px;
    min-height: 32px;
    max-height: 32px;
}

/* Cinta Horizontal de Metricas Cuantitativas */
QFrame#stats_horizontal_panel {
    background-color: rgba(11, 22, 38, 0.75);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 6px;
    min-height: 36px;
    max-height: 40px;
}

QFrame#stats_card_red {
    background-color: rgba(69, 10, 10, 0.45);
    border: 1px solid rgba(239, 68, 68, 0.35);
    border-left: 3px solid #EF4444;
    border-radius: 4px;
}

QFrame#stats_card_green {
    background-color: rgba(6, 78, 59, 0.45);
    border: 1px solid rgba(16, 185, 129, 0.35);
    border-left: 3px solid #10B981;
    border-radius: 4px;
}

QFrame#stats_card_blue {
    background-color: rgba(12, 74, 110, 0.45);
    border: 1px solid rgba(14, 165, 233, 0.35);
    border-left: 3px solid #38BDF8;
    border-radius: 4px;
}

QLabel#stats_card_title_r {
    color: #F87171;
    font-weight: 700;
    font-size: 10.5px;
}

QLabel#stats_card_title_g {
    color: #34D399;
    font-weight: 700;
    font-size: 10.5px;
}

QLabel#stats_card_title_b {
    color: #38BDF8;
    font-weight: 700;
    font-size: 10.5px;
}

QLabel#stats_card_val {
    color: #F1F5F9;
    font-size: 10.5px;
    font-weight: 600;
}

/* Botones Dark Liquid Glass */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0284C7, stop:1 #0369A1);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 5px;
    padding: 4px 11px;
    font-weight: 600;
    font-size: 11.5px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #38BDF8, stop:1 #0284C7);
}

QPushButton:pressed {
    background: #075985;
}

QPushButton:disabled {
    background-color: #1E293B;
    color: #64748B;
}

QPushButton#btn_secondary {
    background: rgba(14, 29, 49, 0.75);
    color: #7DD3FC;
    border: 1px solid rgba(30, 58, 95, 0.85);
}

QPushButton#btn_secondary:hover {
    background: rgba(21, 43, 71, 0.85);
    color: #BAE6FD;
    border-color: #38BDF8;
}

QPushButton#btn_secondary:pressed {
    background: #1A365D;
    color: #FFFFFF;
}

QPushButton#btn_accent {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0891B2, stop:1 #0E7490);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.3);
}

QPushButton#btn_accent:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #06B6D4, stop:1 #0891B2);
}

QPushButton#btn_accent:pressed {
    background: #155E75;
}

QPushButton#btn_tool {
    background: rgba(14, 29, 49, 0.75);
    color: #7DD3FC;
    border: 1px solid rgba(30, 58, 95, 0.85);
    border-radius: 4px;
    padding: 3px 10px;
    font-weight: 600;
    font-size: 11px;
}

QPushButton#btn_tool:hover {
    background: rgba(21, 43, 71, 0.85);
    color: #BAE6FD;
    border-color: #38BDF8;
}

QPushButton#btn_tool:checked {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0284C7, stop:1 #0369A1);
    color: #FFFFFF;
    border-color: #38BDF8;
}

QPushButton#btn_canvas_tool {
    background: rgba(14, 29, 49, 0.85);
    color: #BAE6FD;
    border: 1px solid rgba(56, 189, 248, 0.4);
    border-radius: 3px;
    font-size: 11px;
    font-weight: bold;
    padding: 1px 4px;
}

QPushButton#btn_canvas_tool:hover {
    background: rgba(2, 132, 199, 0.9);
    color: #FFFFFF;
    border-color: #38BDF8;
}

QPushButton#btn_canvas_tool:pressed {
    background: #075985;
}

/* Listas Dark Glass */
QListWidget {
    background-color: rgba(11, 22, 38, 0.75);
    color: #F0F8FF;
    border: 1px solid rgba(30, 58, 95, 0.8);
    border-radius: 6px;
    padding: 3px;
    font-size: 11.5px;
}

QListWidget::item {
    padding: 5px 8px;
    border-radius: 4px;
    border-bottom: 1px solid rgba(14, 30, 51, 0.8);
    color: #F0F8FF;
}

QListWidget::item:selected {
    background-color: rgba(19, 43, 71, 0.85);
    color: #38BDF8;
    font-weight: bold;
    border-left: 3px solid #38BDF8;
}

QListWidget::item:hover:!selected {
    background-color: rgba(15, 34, 56, 0.6);
    color: #BAE6FD;
}

/* Controles de Entrada Dark Glass */
QComboBox {
    background-color: rgba(11, 22, 38, 0.85);
    color: #F0F8FF;
    border: 1px solid rgba(30, 58, 95, 0.85);
    border-radius: 5px;
    padding: 3px 8px;
    min-height: 20px;
    font-size: 11.5px;
}

QComboBox:hover, QComboBox:focus {
    border-color: #38BDF8;
}

QComboBox::drop-down {
    border: none;
    width: 18px;
}

QComboBox QAbstractItemView {
    background-color: #0B1626;
    color: #F0F8FF;
    selection-background-color: #132B47;
    selection-color: #38BDF8;
    border: 1px solid #1E3A5F;
}

QLineEdit {
    background-color: rgba(11, 22, 38, 0.85);
    color: #F0F8FF;
    border: 1px solid rgba(30, 58, 95, 0.85);
    border-radius: 5px;
    padding: 4px 6px;
    font-size: 11.5px;
}

QLineEdit:focus {
    border: 1px solid #38BDF8;
    background-color: #0E2036;
}

/* Sliders Dark Glass Compactos */
QSlider::groove:horizontal {
    height: 4px;
    background: rgba(30, 58, 95, 0.7);
    border-radius: 2px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #38BDF8);
    border-radius: 2px;
}

QSlider::handle:horizontal {
    width: 13px;
    height: 13px;
    margin: -4.5px 0;
    border-radius: 6.5px;
    background: #38BDF8;
    border: 2px solid #0B1626;
}

QSlider::handle:horizontal:hover {
    background: #67E8F9;
}

/* Barra de Estado Dark Glass Compacta */
QStatusBar {
    background-color: rgba(5, 11, 20, 0.85);
    border-top: 1px solid rgba(30, 58, 95, 0.8);
    color: #7DD3FC;
    font-size: 11px;
    font-weight: 500;
}

/* Badges */
QLabel#badge_success {
    background-color: rgba(6, 78, 59, 0.85);
    color: #6EE7B7;
    font-weight: bold;
    padding: 2px 7px;
    border-radius: 4px;
    border: 1px solid #059669;
    font-size: 10.5px;
}

QLabel#badge_warning {
    background-color: rgba(120, 53, 15, 0.85);
    color: #FDE68A;
    font-weight: bold;
    padding: 2px 7px;
    border-radius: 4px;
    border: 1px solid #D97706;
    font-size: 10.5px;
}

/* Badges de Separacion de Canales (Estilo Color Separation) */
QLabel#badge_channel_orig {
    background-color: rgba(30, 41, 59, 0.95);
    color: #E2E8F0;
    font-weight: bold;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid #475569;
    font-size: 11px;
}

QLabel#badge_channel_red {
    background-color: #DC2626;
    color: #FFFFFF;
    font-weight: bold;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid #EF4444;
    font-size: 11px;
}

QLabel#badge_channel_green {
    background-color: #16A34A;
    color: #FFFFFF;
    font-weight: bold;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid #22C55E;
    font-size: 11px;
}

QLabel#badge_channel_blue {
    background-color: #2563EB;
    color: #FFFFFF;
    font-weight: bold;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid #3B82F6;
    font-size: 11px;
}

QPushButton#btn_layout_mode {
    background-color: rgba(15, 23, 42, 0.85);
    color: #7DD3FC;
    border: 1px solid #1E3A5F;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}

QPushButton#btn_layout_mode:checked {
    background-color: #0284C7;
    color: #FFFFFF;
    border: 1px solid #38BDF8;
}
"""

MAIN_STYLESHEET = _LIGHT_STYLESHEET


def get_stylesheet(theme: ThemeMode | str = ThemeMode.LIGHT) -> str:
    """Retorna la hoja de estilos Liquid Glass correspondiente al modo solicitado."""
    if isinstance(theme, str):
        theme_str = theme.lower()
        if theme_str in ("dark", "oscuro"):
            return _DARK_STYLESHEET
        return _LIGHT_STYLESHEET
    elif theme == ThemeMode.DARK:
        return _DARK_STYLESHEET
    return _LIGHT_STYLESHEET
