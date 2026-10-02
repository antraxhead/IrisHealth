"""
Modulo de procesamiento numerico y descomposicion multicanal de bioimagenes.
Opera directamente con arreglos vectorizados NumPy para maximo desempeno.
Incluye pipeline completo de filtros morfologicos, ajuste de luminancia,
control de fases espectrales, pseudocolor (LUT) y computo de histogramas.
"""

from dataclasses import dataclass
from typing import Dict, Tuple, Optional
import numpy as np

from app.constants.strings import STRINGS


class ImageProcessingError(Exception):
    """Excepcion generada en operaciones de procesamiento de bioimagenes."""
    pass


@dataclass
class ChannelStatistics:
    """Estadisticas descriptivas de un canal de bioimagen."""
    name: str
    mean: float
    min: float
    max: float
    std: float

    def formatted(self) -> str:
        """Formatea las estadisticas utilizando la cadena definida en STRINGS."""
        return STRINGS.MULTICHANNEL_STATS_FORMAT.format(
            channel=self.name,
            mean=self.mean,
            min=int(self.min) if isinstance(self.min, (int, np.integer)) or self.min.is_integer() else self.min,
            max=int(self.max) if isinstance(self.max, (int, np.integer)) or self.max.is_integer() else self.max,
            std=self.std,
        )

    def formatted_short(self) -> str:
        """Formatea las estadisticas compactas sin redundancia del nombre del canal."""
        return STRINGS.MULTICHANNEL_STATS_SHORT_FORMAT.format(
            mean=self.mean,
            min=int(self.min) if isinstance(self.min, (int, np.integer)) or self.min.is_integer() else self.min,
            max=int(self.max) if isinstance(self.max, (int, np.integer)) or self.max.is_integer() else self.max,
            std=self.std,
        )


@dataclass
class RGBDecompositionResult:
    """Resultado de la separacion de canales de una bioimagen RGB."""
    original_rgb: np.ndarray             # (H, W, 3) uint8
    red_gray: np.ndarray                 # (H, W) uint8
    green_gray: np.ndarray               # (H, W) uint8
    blue_gray: np.ndarray                # (H, W) uint8
    red_color: np.ndarray                # (H, W, 3) uint8 con solo componente R
    green_color: np.ndarray              # (H, W, 3) uint8 con solo componente G
    blue_color: np.ndarray               # (H, W, 3) uint8 con solo componente B
    stats_red: ChannelStatistics
    stats_green: ChannelStatistics
    stats_blue: ChannelStatistics


class ImageProcessor:
    """Motor cientifico de analisis, filtrado y descomposicion de bioimagenes."""

    @staticmethod
    def calculate_channel_stats(channel_data: np.ndarray, channel_name: str) -> ChannelStatistics:
        """Calcula estadisticas basicas sobre la matriz de un canal."""
        return ChannelStatistics(
            name=channel_name,
            mean=float(np.mean(channel_data)),
            min=float(np.min(channel_data)),
            max=float(np.max(channel_data)),
            std=float(np.std(channel_data)),
        )

    @classmethod
    def decompose_rgb(cls, image_array: np.ndarray) -> RGBDecompositionResult:
        """
        Descompone una imagen RGB (H, W, 3) en sus componentes R, G y B.
        Genera tanto versiones en escala de grises de intensidad como versiones filtradas a color.
        """
        if not isinstance(image_array, np.ndarray):
            reason = "El argumento debe ser un arreglo NumPy."
            raise ImageProcessingError(STRINGS.ERR_PROCESS_FAILED.format(reason=reason))

        if image_array.dtype != np.uint8:
            normalized = np.clip(image_array, 0, 255).astype(np.uint8)
        else:
            normalized = image_array

        if normalized.ndim == 2:
            rgb_base = np.stack([normalized, normalized, normalized], axis=-1)
        elif normalized.ndim == 3:
            if normalized.shape[2] == 1:
                gray = normalized[:, :, 0]
                rgb_base = np.stack([gray, gray, gray], axis=-1)
            elif normalized.shape[2] >= 3:
                rgb_base = normalized[:, :, :3]
            else:
                gray = normalized[:, :, 0]
                rgb_base = np.stack([gray, gray, gray], axis=-1)
        else:
            reason = "La imagen no tiene dimensiones validas para descomposicion."
            raise ImageProcessingError(STRINGS.ERR_PROCESS_FAILED.format(reason=reason))

        height, width, _ = rgb_base.shape

        r_gray = np.ascontiguousarray(rgb_base[:, :, 0])
        g_gray = np.ascontiguousarray(rgb_base[:, :, 1])
        b_gray = np.ascontiguousarray(rgb_base[:, :, 2])

        # Generacion de placas de separacion de color RGB autenticas (Color Separation Plates)
        # Analogas al estandar de separacion grafica CMYK pero en el espacio aditivo RGB.
        mean_lum = float(np.mean(rgb_base))
        if mean_lum >= 64.0:
            # Bioimagenes de campo claro (histologia, citologia, frotis) y fotografia general:
            # Preserva la neutralidad y claridad del fondo microscopico/altas luces mientras
            # modula la densidad cromatica especifica del canal sobre el tejido biologico.
            def _make_separation_plate(chan_data: np.ndarray, c_dark: np.ndarray, c_mid: np.ndarray, c_light: np.ndarray) -> np.ndarray:
                t = chan_data.astype(float) / 255.0
                plate = np.zeros((*chan_data.shape, 3), dtype=np.uint8)
                mask_low = t < 0.5
                t_low = (t[mask_low] / 0.5)[:, np.newaxis]
                plate[mask_low] = np.clip(c_dark + (c_mid - c_dark) * t_low, 0, 255).astype(np.uint8)
                mask_high = ~mask_low
                t_high = ((t[mask_high] - 0.5) / 0.5)[:, np.newaxis]
                plate[mask_high] = np.clip(c_mid + (c_light - c_mid) * t_high, 0, 255).astype(np.uint8)
                return plate

            r_color = _make_separation_plate(
                r_gray,
                np.array([160.0, 10.0, 25.0]),
                np.array([235.0, 35.0, 45.0]),
                np.array([255.0, 240.0, 242.0])
            )
            g_color = _make_separation_plate(
                g_gray,
                np.array([15.0, 120.0, 35.0]),
                np.array([30.0, 195.0, 55.0]),
                np.array([240.0, 255.0, 242.0])
            )
            b_color = _make_separation_plate(
                b_gray,
                np.array([20.0, 50.0, 170.0]),
                np.array([35.0, 95.0, 235.0]),
                np.array([240.0, 245.0, 255.0])
            )
        else:
            # Bioimagenes de campo oscuro o fluorescencia multiespectral:
            # Conserva fondo negro puro [0, 0, 0] y emision fluoroforica en banda espectral pura.
            r_color = np.zeros((height, width, 3), dtype=np.uint8)
            r_color[:, :, 0] = r_gray
            g_color = np.zeros((height, width, 3), dtype=np.uint8)
            g_color[:, :, 1] = g_gray
            b_color = np.zeros((height, width, 3), dtype=np.uint8)
            b_color[:, :, 2] = b_gray

        stats_r = cls.calculate_channel_stats(r_gray, STRINGS.MULTICHANNEL_CHANNEL_RED)
        stats_g = cls.calculate_channel_stats(g_gray, STRINGS.MULTICHANNEL_CHANNEL_GREEN)
        stats_b = cls.calculate_channel_stats(b_gray, STRINGS.MULTICHANNEL_CHANNEL_BLUE)

        return RGBDecompositionResult(
            original_rgb=rgb_base,
            red_gray=r_gray,
            green_gray=g_gray,
            blue_gray=b_gray,
            red_color=r_color,
            green_color=g_color,
            blue_color=b_color,
            stats_red=stats_r,
            stats_green=stats_g,
            stats_blue=stats_b,
        )

    @classmethod
    def apply_pipeline(
        cls,
        image_array: np.ndarray,
        brightness: int = 0,
        contrast: float = 1.0,
        gamma: float = 1.0,
        phase_red: float = 1.0,
        phase_green: float = 1.0,
        phase_blue: float = 1.0,
        spatial_filter: str = "none",
        lut_mode: str = "natural",
    ) -> np.ndarray:
        """
        Ejecuta el pipeline completo de procesamiento cientifico sobre la bioimagen:
        1. Fases de color (ganancias independientes R, G, B).
        2. Brillo y contraste (escalamiento lineal).
        3. Correccion gamma (mapeo exponencial no lineal).
        4. Filtros espaciales (Enfoque, Gaussiano, Sobel, Inversion).
        5. Mapeo de pseudocolor (LUT).
        """
        if image_array is None or not isinstance(image_array, np.ndarray):
            return np.zeros((100, 100, 3), dtype=np.uint8)

        img = image_array.astype(np.float32)

        # 1. Control de Fases de Color
        if img.ndim == 3 and img.shape[2] >= 3:
            img[:, :, 0] *= phase_red
            img[:, :, 1] *= phase_green
            img[:, :, 2] *= phase_blue

        # 2. Brillo y Contraste: Out = (In - 128) * contrast + 128 + brightness
        if contrast != 1.0 or brightness != 0:
            img = (img - 127.5) * contrast + 127.5 + float(brightness)

        img = np.clip(img, 0.0, 255.0)

        # 3. Correccion Gamma: Out = 255 * (In / 255) ^ (1 / gamma)
        if gamma != 1.0 and gamma > 0.01:
            norm = img / 255.0
            img = 255.0 * np.power(norm, 1.0 / gamma)
            img = np.clip(img, 0.0, 255.0)

        result_uint8 = img.astype(np.uint8)

        # 4. Filtros Espaciales y Morfologicos
        if spatial_filter != "none":
            result_uint8 = cls._apply_spatial_filter(result_uint8, spatial_filter)

        # 5. Mapeo de Pseudocolor (LUT)
        if lut_mode != "natural":
            result_uint8 = cls._apply_pseudocolor(result_uint8, lut_mode)

        return result_uint8

    @classmethod
    def _apply_spatial_filter(cls, image: np.ndarray, filter_type: str) -> np.ndarray:
        """Aplica convoluciones o transformaciones espaciales optimizadas en NumPy."""
        h, w = image.shape[:2]
        is_color = (image.ndim == 3 and image.shape[2] >= 3)

        if filter_type == "invert":
            return 255 - image

        # Operaciones por canal
        def convolve2d_fast(channel: np.ndarray, kernel: np.ndarray) -> np.ndarray:
            kh, kw = kernel.shape
            pad_h, pad_w = kh // 2, kw // 2
            padded = np.pad(channel.astype(np.float32), ((pad_h, pad_h), (pad_w, pad_w)), mode="edge")
            # Convolucion matricial vectorizada 3x3
            out = np.zeros_like(channel, dtype=np.float32)
            for i in range(kh):
                for j in range(kw):
                    out += kernel[i, j] * padded[i:i + h, j:j + w]
            return out

        if filter_type == "sharpen":
            # Kernel de realce de enfoque laplaciano
            kernel = np.array([
                [ 0.0, -1.0,  0.0],
                [-1.0,  5.0, -1.0],
                [ 0.0, -1.0,  0.0]
            ], dtype=np.float32)

            if is_color:
                chans = [convolve2d_fast(image[:, :, c], kernel) for c in range(3)]
                out = np.stack(chans, axis=-1)
            else:
                out = convolve2d_fast(image, kernel)
            return np.clip(out, 0, 255).astype(np.uint8)

        elif filter_type == "blur":
            # Kernel Gaussiano normalizado 3x3
            kernel = np.array([
                [1.0 / 16.0, 2.0 / 16.0, 1.0 / 16.0],
                [2.0 / 16.0, 4.0 / 16.0, 2.0 / 16.0],
                [1.0 / 16.0, 2.0 / 16.0, 1.0 / 16.0]
            ], dtype=np.float32)

            if is_color:
                chans = [convolve2d_fast(image[:, :, c], kernel) for c in range(3)]
                out = np.stack(chans, axis=-1)
            else:
                out = convolve2d_fast(image, kernel)
            return np.clip(out, 0, 255).astype(np.uint8)

        elif filter_type == "sobel":
            # Operador de gradiente Sobel para extraccion de contornos celulares
            gx_k = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
            gy_k = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)

            # Convertir a luminancia para gradiente unificado
            if is_color:
                lum = 0.299 * image[:, :, 0] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 2]
            else:
                lum = image.astype(np.float32)

            gx = convolve2d_fast(lum, gx_k)
            gy = convolve2d_fast(lum, gy_k)
            magnitude = np.hypot(gx, gy)
            norm_mag = np.clip(magnitude, 0, 255).astype(np.uint8)

            # Devolver como imagen tricromatica con tinte cyan para realce visual
            out = np.zeros((h, w, 3), dtype=np.uint8)
            out[:, :, 0] = (norm_mag * 0.2).astype(np.uint8)
            out[:, :, 1] = (norm_mag * 0.8).astype(np.uint8)
            out[:, :, 2] = norm_mag
            return out

        return image

    @classmethod
    def _apply_pseudocolor(cls, image: np.ndarray, lut_mode: str) -> np.ndarray:
        """Aplica tablas de busqueda de color (LUT) clinicas."""
        h, w = image.shape[:2]
        if image.ndim == 3 and image.shape[2] >= 3:
            lum = (0.299 * image[:, :, 0] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 2]).astype(np.uint8)
        else:
            lum = image.astype(np.uint8)

        if lut_mode == "grayscale":
            return np.stack([lum, lum, lum], axis=-1)

        norm = lum.astype(np.float32) / 255.0

        if lut_mode == "fluorescence":
            # DAPI (Azul para intensidades bajas-medias) y FITC (Verde para medias-altas)
            out = np.zeros((h, w, 3), dtype=np.uint8)
            out[:, :, 2] = np.clip(np.sin(norm * np.pi) * 255.0 * 1.2, 0, 255).astype(np.uint8)
            out[:, :, 1] = np.clip((norm ** 1.3) * 255.0, 0, 255).astype(np.uint8)
            out[:, :, 0] = np.clip((norm ** 3.0) * 200.0, 0, 255).astype(np.uint8)
            return out

        elif lut_mode == "thermal":
            # Gradiente termico continuo: Negro -> Morado -> Cyan -> Amarillo -> Blanco
            out = np.zeros((h, w, 3), dtype=np.uint8)
            out[:, :, 0] = np.clip((np.sin(norm * np.pi * 1.5 - 0.5) * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
            out[:, :, 1] = np.clip((np.sin(norm * np.pi * 2.0 - 1.5) * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
            out[:, :, 2] = np.clip((np.cos(norm * np.pi * 1.2) * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
            return out

        return image

    @staticmethod
    def calculate_histogram(image_array: np.ndarray) -> Dict[str, np.ndarray]:
        """Calcula la distribucion de frecuencias (histograma) para los 256 niveles de intensidad."""
        if image_array is None or not isinstance(image_array, np.ndarray) or image_array.size == 0:
            zeros = np.zeros(256, dtype=np.int32)
            return {"r": zeros, "g": zeros, "b": zeros, "lum": zeros}

        arr = np.clip(image_array, 0, 255).astype(np.uint8)

        if arr.ndim == 3 and arr.shape[2] >= 3:
            r_hist = np.bincount(arr[:, :, 0].ravel(), minlength=256)[:256]
            g_hist = np.bincount(arr[:, :, 1].ravel(), minlength=256)[:256]
            b_hist = np.bincount(arr[:, :, 2].ravel(), minlength=256)[:256]
            lum = (0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]).astype(np.uint8)
            lum_hist = np.bincount(lum.ravel(), minlength=256)[:256]
        else:
            flat = arr.ravel()
            lum_hist = np.bincount(flat, minlength=256)[:256]
            r_hist, g_hist, b_hist = lum_hist, lum_hist, lum_hist

        return {
            "r": r_hist,
            "g": g_hist,
            "b": b_hist,
            "lum": lum_hist,
        }

    @staticmethod
    def dynamic_range_adjustment(image_array: np.ndarray, min_in: int, max_in: int) -> np.ndarray:
        """
        Ajusta el rango dinamico de la imagen mapeando min_in a 0 y max_in a 255.
        Valores fuera de [min_in, max_in] son truncados.
        """
        if image_array is None or not isinstance(image_array, np.ndarray):
            return np.zeros((10, 10, 3), dtype=np.uint8)

        img_float = image_array.astype(np.float32)
        
        # Mapeo lineal
        range_in = float(max_in - min_in)
        if range_in == 0:
            range_in = 1.0  # Evitar division por cero

        img_float = ((img_float - min_in) / range_in) * 255.0
        
        return np.clip(img_float, 0, 255).astype(np.uint8)

    @staticmethod
    def combine_rgb_images(img1: np.ndarray, img2: np.ndarray, r1: float, r2: float, g1: float, g2: float, b1: float, b2: float) -> np.ndarray:
        """
        Combina dos imagenes RGB usando porcentajes dados para cada canal.
        r1, r2, g1, g2, b1, b2 deben ser valores entre 0 y 1.
        """
        if img1 is None or img2 is None:
            return np.zeros((10, 10, 3), dtype=np.uint8)

        # Asegurar mismos tamanos
        h = min(img1.shape[0], img2.shape[0])
        w = min(img1.shape[1], img2.shape[1])
        
        i1 = img1[:h, :w].astype(np.float32)
        i2 = img2[:h, :w].astype(np.float32)

        out = np.zeros((h, w, 3), dtype=np.float32)

        # Si alguna es escala de grises, convertirla
        if i1.ndim == 2:
            i1 = np.stack([i1, i1, i1], axis=-1)
        elif i1.ndim == 3 and i1.shape[2] == 1:
            i1 = np.concatenate([i1, i1, i1], axis=-1)
            
        if i2.ndim == 2:
            i2 = np.stack([i2, i2, i2], axis=-1)
        elif i2.ndim == 3 and i2.shape[2] == 1:
            i2 = np.concatenate([i2, i2, i2], axis=-1)

        out[:, :, 0] = i1[:, :, 0] * r1 + i2[:, :, 0] * r2
        out[:, :, 1] = i1[:, :, 1] * g1 + i2[:, :, 1] * g2
        out[:, :, 2] = i1[:, :, 2] * b1 + i2[:, :, 2] * b2

        return np.clip(out, 0, 255).astype(np.uint8)

    @staticmethod
    def numpy_to_qimage(array: np.ndarray):
        """Convierte un arreglo NumPy a un objeto PySide6 QImage de forma segura."""
        from PySide6.QtGui import QImage

        if array is None:
            return QImage()

        arr = np.ascontiguousarray(array, dtype=np.uint8)
        if arr.ndim == 2:
            height, width = arr.shape
            bytes_per_line = width
            q_img = QImage(arr.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8)
            return q_img.copy()
        elif arr.ndim == 3 and arr.shape[2] == 3:
            height, width, channels = arr.shape
            bytes_per_line = 3 * width
            q_img = QImage(arr.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            return q_img.copy()
        elif arr.ndim == 3 and arr.shape[2] == 4:
            height, width, channels = arr.shape
            bytes_per_line = 4 * width
            q_img = QImage(arr.data, width, height, bytes_per_line, QImage.Format.Format_RGBA8888)
            return q_img.copy()
        else:
            reason = f"Dimensiones no soportadas para conversion a QImage: {arr.shape}"
            raise ImageProcessingError(STRINGS.ERR_PROCESS_FAILED.format(reason=reason))
