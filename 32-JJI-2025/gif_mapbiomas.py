# %% - Cria PNGs (SEM TEXTO)
import os
import rasterio
import numpy as np
from rasterio.plot import show
import matplotlib.pyplot as plt

# Define the path to your TIFF files
caminho_tiffs = "C:/Users/mateu/OneDrive/Projetos/arapressao/0-dados_globais/dados_processados/tiffs/usos_arapressao-1985-2024"

# Define the color mapping
json_cores = {
    "1": "#1f8d49", "2": "#ffffff", "3": "#1f8d49", "4": "#7dc975", "5": "#04f8fd",
    "6": "#007785", "7": "#ffffff", "8": "#ffffff", "9": "#7a5900", "10": "#d6bc74",
    "11": "#519799", "12": "#d6bc74", "13": "#ffffff", "14": "#ffefc3", "15": "#edde8e",
    "16": "#ffffff", "17": "#ffffff", "18": "#f974ed", "19": "#c27ba0", "20": "#db7093",
    "21": "#ffefc3", "22": "#d4271e", "23": "#ffa07a", "24": "#d4271e", "25": "#db4644",
    "26": "#2532e4", "27": "#ffffff", "28": "#ffffff", "29": "#ffaa5f", "30": "#9c0027",
    "31": "#091077", "32": "#fc8114", "33": "#2532e4", "34": "#ffffff", "35": "#9065d0",
    "36": "#d082de", "37": "#ffffff", "38": "#ffffff", "39": "#f5b3c8", "40": "#c71585",
    "41": "#f54ca9", "42": "#ffffff", "43": "#ffffff", "44": "#ffffff", "45": "#ffffff",
    "46": "#d68fe2", "47": "#9932cc", "48": "#e6ccff", "49": "#02d659", "50": "#ad5100",
    "51": "#ffffff", "52": "#ffffff", "53": "#ffffff", "54": "#ffffff", "55": "#ffffff",
    "56": "#ffffff", "57": "#ffffff", "58": "#ffffff", "59": "#ffffff", "60": "#ffffff",
    "61": "#ffffff", "62": "#ff69b4", "63": "#ffffff", "64": "#ffffff", "65": "#ffffff",
    "66": "#ffffff", "67": "#ffffff", "68": "#ffffff", "69": "#ffffff", "70": "#ffffff",
    "71": "#ffffff", "72": "#ffffff", "73": "#ffffff", "74": "#ffffff", "75": "#c12100"
}

# Function to convert hex color to RGB tuple
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Create a color mapping array
color_map = {}
for key, hex_color in json_cores.items():
    color_map[int(key)] = hex_to_rgb(hex_color)

# Primeiro, apague todas as PNGs existentes para recriar limpas
png_dir = 'C:/Users/mateu/OneDrive/Projetos/arapressao/4-augm_arima/resultados/mapbiomas_sp-frames'
for file in os.listdir(png_dir):
    if file.endswith('.png'):
        os.remove(os.path.join(png_dir, file))

for year in range(1985, 2025):
    with rasterio.Env():
        tiff_path = f"{caminho_tiffs}/MB-AraPresSao_{year}.tif"
        png_path = f'{png_dir}/{year}_frame.png'
        
        if not os.path.exists(tiff_path):
            print(f"TIFF file for year {year} does not exist, skipping.")
            continue
            
        print(f"Creating PNG for year {year}...")
        with rasterio.open(tiff_path) as src:
            Z = src.read(1)
            meta = src.meta
            # Create RGB array
            rgb_array = np.zeros((Z.shape[0], Z.shape[1], 3), dtype=np.uint8)
            # Apply color mapping
            for value, rgb in color_map.items():
                mask = Z == value
                rgb_array[mask] = rgb
            # Update metadata for RGB PNG
            meta.update({
                'driver': 'PNG',
                'dtype': 'uint8',
                'count': 3,  # RGB has 3 bands
                'nodata': 0
            })
        
        # Write RGB image (SEM TEXTO)
        with rasterio.open(png_path, 'w', **meta) as dst:
            dst.write(rgb_array[:, :, 0], 1)  # Red band
            dst.write(rgb_array[:, :, 1], 2)  # Green band
            dst.write(rgb_array[:, :, 2], 3)  # Blue band
        
        # Remove .aux.xml created
        if os.path.exists(png_path + '.aux.xml'):
            os.remove(png_path + '.aux.xml')

# %% - Cria o GIF (ADICIONA TEXTO APENAS AQUI)
from PIL import Image, ImageDraw, ImageFont
import os

Image.MAX_IMAGE_PIXELS = None

gif_path = f'{png_dir}/animation.gif'

def create_gif_with_text(input_dir, output_gif_path, max_size=800):
    """Create GIF from PNGs, adding text only during GIF creation"""
    
    png_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.png')])
    n_frames = len(png_files)
    
    # Fonte para texto
    try:
        font = ImageFont.truetype("arial.ttf", 30)  # Aumentei o tamanho para melhor visibilidade
    except:
        font = ImageFont.load_default()
    
    print("Creating GIF with annotations...")
    images = []
    
    for i, filename in enumerate(png_files):
        print(f"Processing {i+1}/{n_frames}: {filename}")
        img_path = os.path.join(input_dir, filename)
        
        # Abre a imagem ORIGINAL (sem texto)
        with Image.open(img_path) as img:
            # Redimensiona
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Cria uma cópia para desenhar (evita modificar a original)
            img_with_text = img.copy()
            draw = ImageDraw.Draw(img_with_text)
            
            # Extrair ano do nome do arquivo
            year = filename.split("_")[0]
            
            # Adiciona ano (canto superior esquerdo)
            draw.text((10, 10), year, font=font, fill="white")
            
            # Adiciona borda ao texto para melhor contraste
            draw.text((9, 9), year, font=font, fill="black")
            draw.text((11, 9), year, font=font, fill="black")
            draw.text((9, 11), year, font=font, fill="black")
            draw.text((11, 11), year, font=font, fill="black")
            draw.text((10, 10), year, font=font, fill="white")
            
            # Adicionar contagem regressiva com pontos
            dots = ""
            if i == n_frames - 3:
                dots = "..."
            elif i == n_frames - 2:
                dots = ".."
            elif i == n_frames - 1:
                dots = "."
            
            if dots:
                w, h = img_with_text.size
                bbox = draw.textbbox((0, 0), dots, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
                
                # Adiciona borda aos pontos também
                draw.text((w - text_w - 12, h - text_h - 12), dots, font=font, fill="black")
                draw.text((w - text_w - 8, h - text_h - 12), dots, font=font, fill="black")
                draw.text((w - text_w - 12, h - text_h - 8), dots, font=font, fill="black")
                draw.text((w - text_w - 8, h - text_h - 8), dots, font=font, fill="black")
                draw.text((w - text_w - 10, h - text_h - 10), dots, font=font, fill="white")
            
            images.append(img_with_text.copy())
    
    # Save GIF
    print("Saving GIF...")
    images[0].save(
        output_gif_path, 
        save_all=True, 
        append_images=images[1:], 
        duration=300,  # 300ms = 0.3s por frame
        loop=0, 
        optimize=True
    )
    
    print(f"GIF saved to: {output_gif_path}")

# Usage
create_gif_with_text(png_dir, gif_path, max_size=800)