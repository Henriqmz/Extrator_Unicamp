import os
import sys
import re
import fitz

BASE_DIR = r"C:/Users/tocoa/OneDrive/Área de Trabalho/Ike/Projeto"
sys.path.insert(0, BASE_DIR)

from extractor import *
from processor import *

PDF_PATH = os.path.join(BASE_DIR, "Provas", "1-provas-e-gabaritos-unicamp-2021", "1ª fase", "Provas E e G.pdf")
doc = fitz.open(PDF_PATH)
page = doc[20] # index 20 é a Página 21

mid_x = page.rect.width / 2

# Obter linhas de texto
left_lines, right_lines = linhas_por_coluna(page, mid_x)

print("=== COLUNA ESQUERDA ===")
for l in left_lines:
    print(f"Y={l['y']:.2f}: {repr(l['texto'])}")

print("\n=== COLUNA DIREITA ===")
for l in right_lines:
    print(f"Y={l['y']:.2f}: {repr(l['texto'])}")

# Obter imagens geradas para a página 20
# Vamos rodar extrair_imagens na página 20
temp_dir = os.path.join(BASE_DIR, "scratch", "temp_p20")
os.makedirs(temp_dir, exist_ok=True)
new_doc = fitz.open()
new_doc.insert_pdf(doc, from_page=20, to_page=20)
imagens = extrair_imagens(new_doc, output_dir=temp_dir, prefixo="debug_p20")

print("\n=== IMAGENS EXTRAÍDAS ===")
for img in imagens:
    print(f"Arquivo: {os.path.basename(img['arquivo'])}, Y={img['y']:.2f}, X={img['x']:.2f}, W={img['largura']:.2f}")
