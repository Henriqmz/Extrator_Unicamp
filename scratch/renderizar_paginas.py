import os
import sys
import fitz

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_PATH = os.path.join(BASE_DIR, "Provas", "1-provas-e-gabaritos-unicamp-2021", "1ª fase", "Provas E e G.pdf")
OUTPUT_DIR = os.path.join(BASE_DIR, "scratch")

os.makedirs(OUTPUT_DIR, exist_ok=True)
doc = fitz.open(PDF_PATH)

# Renderizar página 6 (Questão 18 e imagem da OMS)
page_6 = doc[6] # index 6 é a Página 7 física do PDF
pix_6 = page_6.get_pixmap(matrix=fitz.Matrix(2, 2))
output_path_6 = os.path.join(OUTPUT_DIR, "pagina_6_2021.png")
pix_6.save(output_path_6)
print(f"Página 6 salva em: {output_path_6}")

# Renderizar página 7 (Questão 20 e imagens nas alternativas)
page_7 = doc[7] # index 7 é a Página 8 física do PDF
pix_7 = page_7.get_pixmap(matrix=fitz.Matrix(2, 2))
output_path_7 = os.path.join(OUTPUT_DIR, "pagina_7_2021.png")
pix_7.save(output_path_7)
print(f"Página 7 salva em: {output_path_7}")
