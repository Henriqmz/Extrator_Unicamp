import os
import sys
import re
import fitz

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from extractor import *
from processor import *

PDF_PATH = os.path.join(BASE_DIR, "Provas", "1-provas-e-gabaritos-unicamp-2021", "1ª fase", "Provas E e G.pdf")

doc = fitz.open(PDF_PATH)

# Vamos descobrir em qual página está a QUESTÃO 18
target_page_idx = None
for idx, page in enumerate(doc):
    text = page.get_text()
    if "QUESTÃO 18" in text:
        target_page_idx = idx
        print(f"QUESTÃO 18 encontrada na página index: {idx} (Página {idx+1})")
        break

if target_page_idx is not None:
    page = doc[target_page_idx]
    mid_x = page.rect.width / 2
    
    # Rodar a mesma lógica de obtenção de elementos de processor.py
    left_lines, right_lines = linhas_por_coluna(page, mid_x)
    
    print("\n--- ELEMENTOS DA ESQUERDA ---")
    for line in left_lines:
        print(f"Y={line['y']:.2f}: {repr(line['texto'][:60])}")
        
    print("\n--- ELEMENTOS DA DIREITA ---")
    for line in right_lines:
        print(f"Y={line['y']:.2f}: {repr(line['texto'][:60])}")

    # Imagens da página
    print("\n--- IMAGENS EXTRAÍDAS DA PÁGINA ---")
    # Vamos rodar extrair_imagens apenas para esta página
    # Para isso, criamos uma pasta temporária
    temp_img_dir = os.path.join(BASE_DIR, "scratch", "temp_imgs_debug")
    os.makedirs(temp_img_dir, exist_ok=True)
    
    # Criar um doc de uma única página
    new_doc = fitz.open()
    new_doc.insert_pdf(doc, from_page=target_page_idx, to_page=target_page_idx)
    imagens = extrair_imagens(new_doc, output_dir=temp_img_dir, prefixo="debug_page")
    for img in imagens:
        print(f"Imagem: x={img.get('x'):.2f}, y={img.get('y'):.2f}, w={img.get('largura'):.2f}, arquivo={img['arquivo']}")
