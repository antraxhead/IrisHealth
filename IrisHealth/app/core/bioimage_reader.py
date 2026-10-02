"""
Modulo para lectura, validacion y extraccion de metadatos de bioimagenes.
Utiliza Pillow y NumPy para un acceso eficiente y seguro a los datos de imagen.
Todas las cadenas de texto son importadas desde app.constants.strings.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, List
import numpy as np
from PIL import Image

try:
    import pydicom
    HAS_PYDICOM = True
except ImportError:
    HAS_PYDICOM = False

from app.constants.strings import STRINGS


class BioImageError(Exception):
    """Excepcion base para operaciones con bioimagenes."""
    pass


class BioImageLoadError(BioImageError):
    """Excepcion al fallar la carga de una bioimagen."""
    pass


@dataclass
class BioImageMetadata:
    """Contenedor de metadatos de una bioimagen."""
    filename: str
    filepath: str
    width: int
    height: int
    channels: int
    color_mode: str
    dtype: str
    file_size_bytes: int
    is_color: bool

    def formatted_summary(self) -> str:
        """Devuelve un resumen formateado de los metadatos sin cadenas hardcodeadas."""
        size_kb = self.file_size_bytes / 1024.0
        lines = [
            STRINGS.META_FILENAME.format(filename=self.filename),
            STRINGS.META_DIMENSIONS.format(width=self.width, height=self.height),
            STRINGS.META_CHANNELS.format(channels=self.channels, color_mode=self.color_mode),
            STRINGS.META_DTYPE.format(dtype=self.dtype),
            STRINGS.META_SIZE_BYTES.format(size_kb=size_kb),
        ]
        return "\n".join(lines)


@dataclass
class BioImageItem:
    """Estructura completa de una bioimagen con sus arreglos de datos."""
    metadata: BioImageMetadata
    original_array: np.ndarray  # Arreglo en formato RGB uint8 de forma (H, W, 3) o (H, W)


class BioImageReader:
    """Lector y validador de archivos de bioimagenes."""

    SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".dcm"}

    @classmethod
    def load_from_zip(cls, filepath: str | Path) -> List['BioImageItem']:
        """Carga multiples bioimagenes desde un archivo comprimido ZIP."""
        import zipfile
        import io
        path = Path(filepath)
        items = []
        if not path.is_file() or path.suffix.lower() != ".zip":
            raise BioImageLoadError(f"Archivo ZIP no valido: {path}")

        try:
            with zipfile.ZipFile(path, 'r') as zf:
                for zip_info in zf.infolist():
                    if zip_info.is_dir():
                        continue
                    
                    filename_path = Path(zip_info.filename)
                    if filename_path.name.startswith("._"):
                        continue
                        
                    suffix = filename_path.suffix.lower()
                    if suffix in cls.SUPPORTED_EXTENSIONS:
                        with zf.open(zip_info) as f:
                            file_bytes = f.read()
                            
                        try:
                            if suffix == ".dcm":
                                if not HAS_PYDICOM:
                                    continue
                                ds = pydicom.dcmread(io.BytesIO(file_bytes))
                                arr = ds.pixel_array
                                
                                if hasattr(ds, 'RescaleSlope') and hasattr(ds, 'RescaleIntercept'):
                                    arr = arr * float(ds.RescaleSlope) + float(ds.RescaleIntercept)
                                
                                arr = arr.astype(np.float32)
                                arr_min, arr_max = arr.min(), arr.max()
                                if arr_max > arr_min:
                                    arr = (arr - arr_min) / (arr_max - arr_min) * 255.0
                                arr = np.clip(arr, 0, 255).astype(np.uint8)
                                
                                color_mode = "L"
                                width, height = arr.shape[1], arr.shape[0] if arr.ndim >= 2 else (0, 0)
                                if arr.ndim == 2:
                                    arr = np.stack((arr, arr, arr), axis=-1)
                                    color_mode = "RGB"
                            else:
                                with Image.open(io.BytesIO(file_bytes)) as img:
                                    width, height = img.size
                                    orig_mode = img.mode
                                    if orig_mode in ("RGBA", "LA", "P", "CMYK", "YCbCr"):
                                        rgb_img = img.convert("RGB")
                                        color_mode = "RGB"
                                    elif orig_mode == "L":
                                        rgb_img = img.copy()
                                        color_mode = "L"
                                    else:
                                        rgb_img = img.convert("RGB")
                                        color_mode = "RGB"
                                    arr = np.array(rgb_img)

                            if arr.ndim == 2:
                                channels = 1
                                is_color = False
                            elif arr.ndim == 3:
                                channels = arr.shape[2]
                                if channels >= 3:
                                    is_color = not (np.array_equal(arr[:, :, 0], arr[:, :, 1]) and np.array_equal(arr[:, :, 1], arr[:, :, 2]))
                                else:
                                    is_color = False
                            else:
                                channels = 1
                                is_color = False

                            metadata = BioImageMetadata(
                                filename=filename_path.name,
                                filepath=f"{path.name}/{zip_info.filename}",
                                width=width,
                                height=height,
                                channels=channels,
                                color_mode=color_mode,
                                dtype=str(arr.dtype),
                                file_size_bytes=zip_info.file_size,
                                is_color=is_color,
                            )
                            items.append(BioImageItem(metadata=metadata, original_array=arr))
                        except Exception:
                            continue
        except Exception as ex:
            raise BioImageLoadError(f"Error procesando ZIP {path.name}: {ex}")
            
        if not items:
            raise BioImageLoadError(f"No se encontraron imagenes soportadas en {path.name}")
            
        return items

    @classmethod
    def load_from_file(cls, filepath: str | Path) -> BioImageItem:
        """
        Carga una bioimagen desde un archivo local y extrae sus metadatos.
        Normaliza a RGB si la imagen tiene canal alfa o es compatible.
        """
        path = Path(filepath)
        if not path.is_file():
            msg = STRINGS.ERR_LOAD_FAILED.format(filepath=str(path), reason="El archivo no existe.")
            raise BioImageLoadError(msg)

        if path.suffix.lower() not in cls.SUPPORTED_EXTENSIONS:
            msg = STRINGS.ERR_LOAD_FAILED.format(
                filepath=str(path),
                reason=f"Extension '{path.suffix}' no soportada. Formatos validos: {', '.join(cls.SUPPORTED_EXTENSIONS)}"
            )
            raise BioImageLoadError(msg)

        try:
            if path.suffix.lower() == ".dcm":
                if not HAS_PYDICOM:
                    msg = STRINGS.ERR_LOAD_FAILED.format(
                        filepath=str(path), reason="La biblioteca pydicom no esta instalada para leer archivos DICOM."
                    )
                    raise BioImageLoadError(msg)
                
                ds = pydicom.dcmread(str(path))
                arr = ds.pixel_array
                
                # Rescale if needed
                if hasattr(ds, 'RescaleSlope') and hasattr(ds, 'RescaleIntercept'):
                    arr = arr * float(ds.RescaleSlope) + float(ds.RescaleIntercept)
                
                # Convert to float to avoid overflow
                arr = arr.astype(np.float32)
                
                # Normalize to 0-255 uint8 to keep compatibility
                arr_min, arr_max = arr.min(), arr.max()
                if arr_max > arr_min:
                    arr = (arr - arr_min) / (arr_max - arr_min) * 255.0
                arr = np.clip(arr, 0, 255).astype(np.uint8)
                
                color_mode = "L"
                file_size = path.stat().st_size
                width, height = arr.shape[1], arr.shape[0] if arr.ndim >= 2 else (0, 0)
                
                # If grayscale DICOM (most CTs), duplicate channels to simulate RGB for compatibility with existing code
                if arr.ndim == 2:
                    arr = np.stack((arr, arr, arr), axis=-1)
                    color_mode = "RGB"

            else:
                with Image.open(path) as img:
                    file_size = path.stat().st_size
                    width, height = img.size
                    orig_mode = img.mode

                    # Convertir modos como RGBA, CMYK, P a RGB para estandarizar
                    if orig_mode in ("RGBA", "LA"):
                        rgb_img = img.convert("RGB")
                        color_mode = "RGB"
                    elif orig_mode in ("P", "CMYK", "YCbCr"):
                        rgb_img = img.convert("RGB")
                        color_mode = "RGB"
                    elif orig_mode == "L":
                        rgb_img = img.copy()
                        color_mode = "L"
                    else:
                        rgb_img = img.convert("RGB")
                        color_mode = "RGB"

                    arr = np.array(rgb_img)

            if arr.ndim == 2:
                channels = 1
                is_color = False
            elif arr.ndim == 3:
                channels = arr.shape[2]
                # Verificar si realmente hay variacion cromatica o si es gris repetido
                if channels >= 3:
                    is_color = not (np.array_equal(arr[:, :, 0], arr[:, :, 1]) and np.array_equal(arr[:, :, 1], arr[:, :, 2]))
                else:
                    is_color = False
            else:
                channels = 1
                is_color = False

            metadata = BioImageMetadata(
                filename=path.name,
                filepath=str(path.resolve()),
                width=width,
                height=height,
                channels=channels,
                color_mode=color_mode,
                dtype=str(arr.dtype),
                file_size_bytes=file_size,
                is_color=is_color,
            )

            return BioImageItem(metadata=metadata, original_array=arr)

        except Exception as ex:
            msg = STRINGS.ERR_LOAD_FAILED.format(filepath=str(path), reason=str(ex))
            raise BioImageLoadError(msg) from ex
