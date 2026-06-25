import fitz
import re
from extractor import extrair_pdf, linhas_por_coluna

doc = fitz.open("Provas/1-provas-e-gabaritos-unicamp-2021/1ª fase/Provas E e G.pdf")
page = doc[6] # Pag 6
mid_x = page.rect.width / 2

elementos_esquerda = []
elementos_direita = []

left_lines, right_lines = linhas_por_coluna(page, mid_x)
for line in left_lines:
    elementos_esquerda.append({
        "tipo": "texto",
        "y": line["y"],
        "texto": line["texto"]
    })
for line in right_lines:
    elementos_direita.append({
        "tipo": "texto",
        "y": line["y"],
        "texto": line["texto"]
    })

# Obter drawings da página
from extractor import extrair_imagens
import os
import shutil

pasta_temp = "C:/Users/tocoa/OneDrive/Área de Trabalho/Ike/Projeto/temp_debug"
if os.path.exists(pasta_temp):
    shutil.rmtree(pasta_temp)
imgs = extrair_imagens(doc, output_dir=pasta_temp, prefixo="temp")

for img in imgs:
    if img["pagina"] == 6:
        col = "esquerda" if img["x"] < mid_x else "direita"
        el = {
            "tipo": "imagem",
            "y": img["y"],
            "x": img["x"],
            "texto": f"IMAGEM {img['arquivo']}"
        }
        if col == "esquerda":
            elementos_esquerda.append(el)
        else:
            elementos_direita.append(el)

elementos_esquerda.sort(key=lambda x: x["y"])
elementos_direita.sort(key=lambda x: x["y"])

print("ELEMENTOS ESQUERDA:")
for el in elementos_esquerda:
    print(f"y={el['y']:.2f}: {repr(el.get('texto'))}")

print("\nELEMENTOS DIREITA:")
for el in elementos_direita:
    print(f"y={el['y']:.2f}: {repr(el.get('texto'))}")
