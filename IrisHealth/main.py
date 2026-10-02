"""
Punto de entrada principal para IrisHealth - Suite Clinica de Bioimagenes.
Inicia la aplicacion de escritorio PySide6 con configuracion de alta resolucion,
vinculacion del logotipo institucional y tipografia estandar para evitar advertencias de DPI.
"""
#AUTOR: Jose Martin Quiroz Castro
#UNIVERSIDAD DE GUADALAJARA
#Version: 1.0.0

import sys
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import QApplication

from app.constants.strings import STRINGS
from app.constants.paths import get_logo_path
from app.ui.main_window import MainWindow


def main():
    """Inicializa la aplicacion Qt y despliega la ventana principal."""
    app = QApplication(sys.argv)
    app.setApplicationName(STRINGS.APP_NAME)
    app.setApplicationDisplayName(STRINGS.APP_WINDOW_TITLE)

    # Establecer fuente tipografica base del sistema para evitar advertencias de tamano de punto
    app_font = QFont("Segoe UI")
    app_font.setPointSize(10)
    app.setFont(app_font)

    # Establecer icono de aplicacion de forma dinamica si existe el logo
    logo_path = get_logo_path()
    if logo_path.exists():
        app.setWindowIcon(QIcon(str(logo_path)))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

"""Considera que el app fue desarrollada en muy poco tiempo, estare leyendo comentarios de como mejorarla y 
espero solucionar los bugs pronto."""