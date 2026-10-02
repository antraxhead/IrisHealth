"""
Modulo de generacion y gestion de bioimagenes de muestra.
Provee 3 bioimagenes a color sinteticas y calibradas basadas en:
1. Histologia con tincion H&E (Hematoxilina y Eosina).
2. Citologia de frotis sanguineo (eritrocitos y leucocitos).
3. Microscopia de fluorescencia celular (fluoroforos multicolor: GFP verde, DAPI azul, mCherry rojo).
Todas las cadenas de texto se obtienen desde STRINGS.
"""

from pathlib import Path
from typing import List
import numpy as np
from PIL import Image

from app.constants.strings import STRINGS


class SampleBioImageGenerator:
    """Generador de bioimagenes sinteticas calibradas para docencia e investigacion."""

    @staticmethod
    def generate_histology_he(width: int = 400, height: int = 300) -> np.ndarray:
        """
        Genera una bioimagen simulada de tejido histologico con tincion H&E.
        Matices de rosa/magenta (eosina) y violeta profundo (hematoxilina para nucleos).
        """
        np.random.seed(42)
        # Fondo extracelular / estroma eosinofilo (rosa claro)
        base_r = 235 + np.random.randint(-15, 15, (height, width))
        base_g = 185 + np.random.randint(-20, 20, (height, width))
        base_b = 205 + np.random.randint(-15, 15, (height, width))

        # Simular estructuras trabeculares / citoplasma
        y_coords, x_coords = np.ogrid[:height, :width]
        wave = np.sin(x_coords / 25.0) * np.cos(y_coords / 20.0) * 20.0
        base_r = np.clip(base_r + wave, 0, 255)
        base_g = np.clip(base_g + wave * 0.8, 0, 255)

        # Generar nucleos celulares (hematoxilina: azul/violeta intenso, bajo verde, medio rojo)
        num_nuclei = 45
        for _ in range(num_nuclei):
            cx = np.random.randint(20, width - 20)
            cy = np.random.randint(20, height - 20)
            radius = np.random.randint(6, 12)
            dist = np.sqrt((x_coords - cx) ** 2 + (y_coords - cy) ** 2)
            mask = dist <= radius
            halo = (dist <= (radius + 2)) & ~mask

            # Nucleo basofilo
            base_r[mask] = np.random.randint(70, 110)
            base_g[mask] = np.random.randint(30, 60)
            base_b[mask] = np.random.randint(120, 170)

            # Halo citoplasmatico condensado
            base_r[halo] = np.clip(base_r[halo] * 0.8, 0, 255)
            base_g[halo] = np.clip(base_g[halo] * 0.7, 0, 255)

        img = np.stack([base_r, base_g, base_b], axis=-1).astype(np.uint8)
        return img

    @staticmethod
    def generate_blood_smear(width: int = 400, height: int = 300) -> np.ndarray:
        """
        Genera una bioimagen de frotis sanguineo periférico.
        Eritrocitos bicóncavos rosados/rojizos con centro pálido y leucocitos con núcleo lobulado púrpura.
        """
        np.random.seed(101)
        # Fondo de plasma claro ligeramente amarillento/neutro
        base_r = np.full((height, width), 245, dtype=np.float32)
        base_g = np.full((height, width), 242, dtype=np.float32)
        base_b = np.full((height, width), 238, dtype=np.float32)

        y_coords, x_coords = np.ogrid[:height, :width]

        # Eritrocitos (globulos rojos)
        num_rbc = 60
        for _ in range(num_rbc):
            cx = np.random.randint(15, width - 15)
            cy = np.random.randint(15, height - 15)
            radius = np.random.randint(9, 14)
            dist = np.sqrt((x_coords - cx) ** 2 + (y_coords - cy) ** 2)
            mask = dist <= radius

            # Centro palido biconcavo
            center_mask = dist <= (radius * 0.45)
            rim_mask = mask & ~center_mask

            # Borde del eritrocito (rojo anaranjado caracteristico)
            base_r[rim_mask] = 210 + np.random.randint(-10, 10)
            base_g[rim_mask] = 85 + np.random.randint(-10, 10)
            base_b[rim_mask] = 95 + np.random.randint(-10, 10)

            # Centro biconcavo mas palido
            base_r[center_mask] = 230 + np.random.randint(-10, 10)
            base_g[center_mask] = 145 + np.random.randint(-10, 10)
            base_b[center_mask] = 150 + np.random.randint(-10, 10)

        # Leucocito (globulo blanco) con citoplasma palido y nucleo multilobulado purpura
        cx, cy = width // 2, height // 2
        dist_wbc = np.sqrt((x_coords - cx) ** 2 + (y_coords - cy) ** 2)
        wbc_mask = dist_wbc <= 26
        base_r[wbc_mask] = 200
        base_g[wbc_mask] = 190
        base_b[wbc_mask] = 220

        # Lobulos nucleares del leucocito
        for offset in [(-7, -5), (6, -4), (0, 7)]:
            lx = cx + offset[0]
            ly = cy + offset[1]
            dist_l = np.sqrt((x_coords - lx) ** 2 + (y_coords - ly) ** 2)
            lobe_mask = dist_l <= 8
            base_r[lobe_mask] = 75
            base_g[lobe_mask] = 30
            base_b[lobe_mask] = 140

        img = np.stack([
            np.clip(base_r, 0, 255),
            np.clip(base_g, 0, 255),
            np.clip(base_b, 0, 255)
        ], axis=-1).astype(np.uint8)
        return img

    @staticmethod
    def generate_fluorescence_microscopy(width: int = 400, height: int = 300) -> np.ndarray:
        """
        Genera una bioimagen de microscopia de fluorescencia multicanal:
        - Canal Verde (GFP): Filamentos celulares de actina / citoesqueleto.
        - Canal Azul (DAPI): Nucleos celulares marcados.
        - Canal Rojo (mCherry / Mitocondrias): Organelos citoplasmaticos.
        """
        np.random.seed(777)
        # Fondo oscuro tipico de microscopia de fluorescencia
        img_r = np.zeros((height, width), dtype=np.float32)
        img_g = np.zeros((height, width), dtype=np.float32)
        img_b = np.zeros((height, width), dtype=np.float32)

        # Ruido de fondo sensor CCD
        noise = np.random.exponential(scale=3.0, size=(height, width))
        img_r += noise
        img_g += noise
        img_b += noise

        y_coords, x_coords = np.ogrid[:height, :width]

        # 3 Células principales con núcleos DAPI (azul) y filamentos GFP (verde)
        cell_centers = [(width // 4, height // 3), (width * 3 // 4, height // 3), (width // 2, height * 2 // 3)]

        for cx, cy in cell_centers:
            # DAPI: Nucleo azul brillante
            dist_n = np.sqrt((x_coords - cx) ** 2 + (y_coords - cy) ** 2)
            n_intensity = np.exp(- (dist_n ** 2) / (2 * (15 ** 2))) * 230.0
            img_b += n_intensity
            img_g += n_intensity * 0.15

            # Filamentos citoesqueleto (GFP Verde)
            for angle in np.linspace(0, 2 * np.pi, 12, endpoint=False):
                fx = cx + np.cos(angle) * np.linspace(5, 45, 30)
                fy = cy + np.sin(angle) * np.linspace(5, 35, 30)
                for px, py in zip(fx.astype(int), fy.astype(int)):
                    if 0 <= px < width and 0 <= py < height:
                        img_g[max(0, py - 2):min(height, py + 3), max(0, px - 2):min(width, px + 3)] += 35.0

            # Mitocondrias granulares (mCherry Rojo)
            for _ in range(35):
                mx = int(cx + np.random.normal(0, 22))
                my = int(cy + np.random.normal(0, 18))
                if 0 <= mx < width and 0 <= my < height:
                    img_r[max(0, my - 2):min(height, my + 3), max(0, mx - 2):min(width, mx + 3)] += 120.0

        img = np.stack([
            np.clip(img_r, 0, 255),
            np.clip(img_g, 0, 255),
            np.clip(img_b, 0, 255)
        ], axis=-1).astype(np.uint8)
        return img

    @classmethod
    def ensure_sample_images_exist(cls, target_dir: str | Path) -> List[Path]:
        """
        Crea las 3 bioimagenes de muestra en el directorio destino si no existen ya.
        Retorna la lista de rutas a los archivos generados.
        """
        out_dir = Path(target_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        samples = [
            ("bioimagen_01_histologia_tincion_he.png", cls.generate_histology_he),
            ("bioimagen_02_citologia_frotis_sanguineo.png", cls.generate_blood_smear),
            ("bioimagen_03_microscopia_fluorescencia.png", cls.generate_fluorescence_microscopy),
        ]

        saved_paths = []
        for filename, generator_func in samples:
            filepath = out_dir / filename
            if not filepath.exists():
                arr = generator_func()
                Image.fromarray(arr).save(filepath, format="PNG")
            saved_paths.append(filepath)

        return saved_paths
