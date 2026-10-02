"""
Modulo de constantes de texto para la aplicacion IrisHealth BioImaging.
Centraliza todas las cadenas de texto del sistema para evitar cadenas hardcodeadas.
Cumple estrictamente con la directiva de no utilizar emojis.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AppStrings:
    # Identidad y Titulos Institucionales
    APP_NAME: str = "IrisHealth - Suite Clinica de Bioimagenes"
    APP_WINDOW_TITLE: str = "IrisHealth - Sistema Profesional de Analisis y Descomposicion Multicanal de Bioimagenes"
    APP_BRAND_TITLE: str = "IrisHealth"
    APP_BRAND_SUBTITLE: str = "Suite Clinica"
    APP_STATUS_READY: str = "Listo. Seleccione o importe bioimagenes para analisis."
    APP_STATUS_BUSY: str = "Procesando analisis..."

    # Pestanas Principales (Navegacion Integrada)
    TAB_EXPLORER: str = "Explorador de Bioimagenes"
    TAB_MULTICHANNEL: str = "Descomposicion Multicanal"

    # Barra de Herramientas Superior Compacta
    BTN_LOAD_IMAGE: str = "Cargar Bioimagen"
    BTN_LOAD_FOLDER: str = "Importar Carpeta"
    BTN_LOAD_SAMPLES: str = "Cargar Muestras"
    BTN_CLEAR_ALL: str = "Limpiar"
    BTN_EXPORT_PDF: str = "Generar Informe PDF"
    BTN_THEME_DARK: str = "Modo Oscuro"
    BTN_THEME_LIGHT: str = "Modo Claro"
    TOOLTIP_THEME_DARK: str = "Cambiar a la paleta glacial nocturna (tema oscuro)"
    TOOLTIP_THEME_LIGHT: str = "Cambiar a la paleta glacial diurna (tema claro)"
    BTN_CLOSE: str = "Cerrar"
    BTN_CANCEL: str = "Cancelar"
    BTN_ACCEPT: str = "Aceptar"
    BTN_BROWSE: str = "Examinar..."

    # Herramientas de Inspeccion Clinica
    TOOL_ZOOM_IN: str = "Acercar (+)"
    TOOL_ZOOM_OUT: str = "Alejar (-)"
    TOOL_ZOOM_FIT: str = "Ajustar al Marco"
    TOOL_ZOOM_100: str = "Escala 1:1"
    TOOL_PAN: str = "Mano de Paneo"
    TOOL_MEASURE: str = "Regla de Caliper"
    TOOL_EXPORT_PROCESSED: str = "Guardar Imagen"
    TOOL_TOGGLE_PANEL: str = "Panel de Filtros"
    TOOL_PROBE: str = "Sonda de Pixeles"
    TOOL_RESET_VIEW: str = "Restablecer Vista"

    # Seccion Explorador Clinico
    EXPLORER_HEADER_TITLE: str = "Explorador Clinico y Estacion de Trabajo"
    EXPLORER_HEADER_DESC: str = "Exploracion interactiva, navegacion panoramica y medicion celular."
    EXPLORER_LIST_TITLE: str = "Bioimagenes en Serie"
    EXPLORER_COUNT_LABEL: str = "Total en serie: {count}"
    EXPLORER_IMAGE_DETAILS_TITLE: str = "Metadatos de Adquisicion"
    EXPLORER_PREVIEW_TITLE: str = "Visor Principal"
    EXPLORER_NO_SELECTION: str = "Ninguna bioimagen seleccionada en el espacio de trabajo."
    EXPLORER_INSTRUCTION_HINT: str = "Seleccione una bioimagen para iniciar la exploracion interactiva."
    EXPLORER_SERIES_SUFFICIENT: str = "Serie Optima: 3+ bioimagenes."
    EXPLORER_SERIES_INSUFFICIENT: str = "Serie en Proceso: {count} cargadas (min. 3)."

    # Panel de Filtros y Controladores de Fases
    FILTERS_PANEL_TITLE: str = "Filtros y Control de Fases"
    FILTER_GROUP_LUMINANCE: str = "Luminancia y Rango Dinamico"
    FILTER_LABEL_BRIGHTNESS: str = "Brillo: {val:+d}"
    FILTER_LABEL_CONTRAST: str = "Contraste: {val:.2f}x"
    FILTER_LABEL_GAMMA: str = "Gamma: {val:.2f}"
    FILTER_GROUP_COLOR_PHASE: str = "Controladores de Fases de Color"
    FILTER_LABEL_PHASE_RED: str = "Fase Roja: {val:.2f}x"
    FILTER_LABEL_PHASE_GREEN: str = "Fase Verde: {val:.2f}x"
    FILTER_LABEL_PHASE_BLUE: str = "Fase Azul: {val:.2f}x"
    FILTER_GROUP_SPATIAL: str = "Filtros Espaciales"
    FILTER_SPATIAL_NONE: str = "Original (Sin procesar)"
    FILTER_SPATIAL_SHARPEN: str = "Realce de Enfoque (Membranas)"
    FILTER_SPATIAL_BLUR: str = "Filtro Gaussiano (Reduccion Ruido)"
    FILTER_SPATIAL_SOBEL: str = "Bordes Celulares (Sobel)"
    FILTER_SPATIAL_INVERT: str = "Negativo / Inversion"
    FILTER_GROUP_LUT: str = "Mapas de Pseudocolor (LUT)"
    LUT_NATURAL: str = "Tricromatico Natural (RGB)"
    LUT_GRAYSCALE: str = "Escala Monocromatica"
    LUT_FLUORESCENCE: str = "Pseudocolor DAPI / FITC"
    LUT_THERMAL: str = "Gradiente Termico"
    BTN_RESET_FILTERS: str = "Restablecer Filtros"
    HISTOGRAM_TITLE: str = "Histograma de Intensidad"
    HISTOGRAM_CHANNEL_R: str = "Canal R"
    HISTOGRAM_CHANNEL_G: str = "Canal G"
    HISTOGRAM_CHANNEL_B: str = "Canal B"
    HISTOGRAM_CHANNEL_LUM: str = "Luminancia"

    # Sonda de Pixeles y Caliper
    HUD_PROBE_TEXT: str = "Coord: ({x}, {y}) | R: {r} | G: {g} | B: {b} | Lum: {lum}"
    HUD_PROBE_IDLE: str = "Sonda: Mueva el cursor sobre el tejido para leer los valores de intensidad"
    HUD_MEASURE_TEXT: str = "Distancia: {pixels:.1f} px | {microns:.1f} um (aprox.)"
    HUD_MEASURE_HINT: str = "Modo Caliper activo: Arrastre para medir longitud celular"

    # Metadatos Tecnicos de Adquisicion
    META_FILENAME: str = "Archivo: {filename}"
    META_FILEPATH: str = "Ruta local: {filepath}"
    META_DIMENSIONS: str = "Resolucion espacial: {width} x {height} px"
    META_CHANNELS: str = "Canales de color: {channels} ({color_mode})"
    META_DTYPE: str = "Profundidad de adquisicion: {dtype}"
    META_SIZE_BYTES: str = "Tamano de almacenamiento: {size_kb:.2f} KB"

    # Seccion Descomposicion Multicanal y Espectral RGB
    MULTICHANNEL_HEADER_TITLE: str = "Separacion de Color (RGB) y Descomposicion Multicanal"
    MULTICHANNEL_HEADER_DESC: str = "Separacion cuantitativa de bandas espectrales (Rojo, Verde, Azul) para bioimagenes histologicas y microscopicas a color."
    MULTICHANNEL_SELECT_IMAGE_LABEL: str = "Bioimagen activa:"
    MULTICHANNEL_DISPLAY_MODE_LABEL: str = "Modo de presentacion:"
    MULTICHANNEL_MODE_COLOR: str = "Separacion de Color (RGB)"
    MULTICHANNEL_MODE_GRAYSCALE: str = "Proyeccion Monocromatica"
    MULTICHANNEL_LAYOUT_LABEL: str = "Disposicion:"
    MULTICHANNEL_LAYOUT_2X2: str = "Cuadricula (2x2)"
    MULTICHANNEL_LAYOUT_1X4: str = "Tira Horizontal (1x4)"
    MULTICHANNEL_CHANNEL_ORIGINAL: str = "Bioimagen Compuesta (RGB)"
    MULTICHANNEL_CHANNEL_RED: str = "Canal Rojo (Banda R - 630 nm)"
    MULTICHANNEL_CHANNEL_GREEN: str = "Canal Verde (Banda G - 520 nm)"
    MULTICHANNEL_CHANNEL_BLUE: str = "Canal Azul (Banda B - 450 nm)"
    MULTICHANNEL_BADGE_ORIGINAL: str = "Original (RGB)"
    MULTICHANNEL_BADGE_RED: str = "Rojo (Red)"
    MULTICHANNEL_BADGE_GREEN: str = "Verde (Green)"
    MULTICHANNEL_BADGE_BLUE: str = "Azul (Blue)"
    MULTICHANNEL_STATS_TITLE: str = "Metricas Cuantitativas por Canal"
    MULTICHANNEL_STATS_FORMAT: str = "{channel} - Media: {mean:.2f} | Min: {min} | Max: {max} | Desv: {std:.2f}"
    MULTICHANNEL_STATS_SHORT_FORMAT: str = "Media: {mean:.2f} | Min: {min} | Max: {max} | Desv: {std:.2f}"
    MULTICHANNEL_BTN_FIT_ALL: str = "Ajustar Todo"
    MULTICHANNEL_TOOLTIP_FIT_ALL: str = "Ajustar y centrar todas las vistas simultaneamente al tamano de ventana"
    MULTICHANNEL_LABEL_BAND_R: str = "Banda R (630 nm)"
    MULTICHANNEL_LABEL_BAND_G: str = "Banda G (520 nm)"
    MULTICHANNEL_LABEL_BAND_B: str = "Banda B (450 nm)"
    MULTICHANNEL_PROBE_BAND_FORMAT: str = "Coord: ({x}, {y}) | Intensidad {band}: {val}"

    # Dialogo de Generacion de Informes PDF
    PDF_DIALOG_TITLE: str = "Generador de Informes Clinicos y Academicos"
    PDF_DIALOG_HEADER: str = "Emision de Informe Tecnico Documentado"
    PDF_LABEL_LASTNAME: str = "Primer Apellido del Autor:"
    PDF_LABEL_FIRSTNAME: str = "Primer Nombre del Autor:"
    PDF_LABEL_ACTIVITY: str = "Modalidad del Informe:"
    PDF_OPTION_SERIES: str = "Informe de Despliegue de Serie de Bioimagenes (Actividad 2.1)"
    PDF_OPTION_RGB: str = "Informe de Descomposicion Multicanal RGB (Actividad 2.2)"
    PDF_OPTION_DICOM: str = "Informe de Ajuste de Rango Dinamico DICOM CT (Actividad 3.1)"
    PDF_OPTION_COMBINE: str = "Informe de Combinacion de Imagenes Medicas RGB (Actividad 3.2)"
    PDF_LABEL_OUTPUT_DIR: str = "Directorio de destino:"
    PDF_LABEL_PREVIEW_FILENAME: str = "Nombre del archivo resultante:"
    PDF_BTN_GENERATE: str = "Generar Documento PDF"
    PDF_GENERATING: str = "Generando documento PDF..."
    PDF_SUCCESS_TITLE: str = "Informe Emitido Exitosamente"
    PDF_SUCCESS_MESSAGE: str = "El informe ha sido compilado satisfactoriamente en:\n{filepath}"

    # Dialogos de Archivo y Filtros
    FILE_FILTER_BIOIMAGES: str = "Bioimagenes Clinicas (*.png *.jpg *.jpeg *.tif *.tiff *.bmp *.dcm *.zip);;Archivos Comprimidos (*.zip);;Formato DICOM (*.dcm);;Formato TIFF Cientifico (*.tif *.tiff);;Formato PNG Medico (*.png);;Formato JPEG (*.jpg *.jpeg);;Todos los archivos (*.*)"
    FILE_DIALOG_OPEN_IMAGE: str = "Importar Bioimagen Individual"
    FILE_DIALOG_OPEN_FOLDER: str = "Importar Directorio de Serie de Bioimagenes"
    FILE_DIALOG_SAVE_PDF: str = "Guardar Informe PDF"
    FILE_DIALOG_SAVE_PROCESSED: str = "Exportar Bioimagen Procesada"
    FILE_FILTER_EXPORT_IMAGE: str = "Imagen PNG (*.png);;Imagen TIFF (*.tif *.tiff);;Imagen JPEG (*.jpg)"

    # Notificaciones, Validaciones y Errores
    ERR_TITLE: str = "Notificacion de Error"
    WARN_TITLE: str = "Advertencia Clinica"
    INFO_TITLE: str = "Informacion del Sistema"
    ERR_NO_IMAGES_LOADED: str = "No existen bioimagenes cargadas en el espacio de trabajo. Por favor importe archivos primero."
    ERR_LESS_THAN_THREE_IMAGES: str = "Se requieren al menos 3 bioimagenes en la serie para emitir este informe. Actualmente se disponen de {count}."
    ERR_IMAGE_NOT_COLOR: str = "La bioimagen '{name}' carece de componentes tricromaticas (formato monocromatico/grises). El analisis multicanal requiere bioimagenes a color."
    ERR_STUDENT_DATA_REQUIRED: str = "Debe ingresar el Primer Apellido y Primer Nombre del autor para generar el documento oficial."
    ERR_LOAD_FAILED: str = "Error al abrir la bioimagen '{filepath}'. Detalle: {reason}"
    ERR_PROCESS_FAILED: str = "Fallo en el procesamiento de matrices de imagen. Detalle: {reason}"
    ERR_PDF_GENERATION_FAILED: str = "Error al compilar el informe PDF. Detalle: {reason}"
    MSG_SAMPLES_LOADED: str = "Serie de referencia calibrada cargada correctamente (3 bioimagenes)."
    MSG_IMAGE_EXPORTED: str = "Bioimagen exportada exitosamente en:\n{filepath}"

    # Encabezados y Secciones de Informe PDF
    PDF_REPORT_INSTITUTION: str = "IrisHealth - Division de Procesamiento de Bioimagenes"
    PDF_REPORT_DOC_TITLE_21: str = "Informe de Adquisicion y Despliegue de Bioimagenes (Actividad 2.1)"
    PDF_REPORT_DOC_TITLE_22: str = "Informe de Descomposicion Espectral Multicanal RGB (Actividad 2.2)"
    PDF_REPORT_DOC_TITLE_31: str = "Informe de Ajuste de Rango Dinamico en Imagenes DICOM CT (Actividad 3.1)"
    PDF_REPORT_DOC_TITLE_32: str = "Informe de Combinacion de Bioimagenes Medicas RGB (Actividad 3.2)"
    PDF_AUTHOR_LABEL: str = "Autor / Especialista: {lastname}, {firstname}"
    PDF_DATE_LABEL: str = "Fecha de Emision: {date}"
    PDF_CODE_SECTION_TITLE: str = "Algoritmo de Procesamiento Empleado"
    PDF_RESULTS_SECTION_TITLE: str = "Evidencia Visual y Analisis de Resultados"


STRINGS = AppStrings()
