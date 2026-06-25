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

edital, ano, tipo_prova = detectar_edital_ano(PDF_PATH)
paginas, doc = extrair_pdf(PDF_PATH)
pasta_saida = os.path.join(BASE_DIR, "scratch", "temp_trace_q70")
os.makedirs(pasta_saida, exist_ok=True)
imagens = extrair_imagens(doc, output_dir=os.path.join(pasta_saida, "imgs"), prefixo="trace_q70")
texto = extrair_texto(paginas, imagens)
questoes = extrair_questoes(texto, edital=edital, ano=ano, tipo_prova=tipo_prova)

mapa_questoes = {q.metadados.numero: q for q in questoes}
imgs_por_pagina = {}
for img in imagens:
    p = img["pagina"]
    if p not in imgs_por_pagina:
        imgs_por_pagina[p] = []
    imgs_por_pagina[p].append(img)
    
global_elements = []

for page_num in range(len(doc)):
    page = doc[page_num]
    mid_x = page.rect.width / 2
    
    elementos_esquerda = []
    elementos_direita = []
    
    left_lines, right_lines = linhas_por_coluna(page, mid_x)
    for line in left_lines:
        elementos_esquerda.append({
            "tipo": "texto",
            "y": line["y"],
            "texto": line["texto"],
            "pagina": page_num
        })
    for line in right_lines:
        elementos_direita.append({
            "tipo": "texto",
            "y": line["y"],
            "texto": line["texto"],
            "pagina": page_num
        })
                    
    page_imgs = imgs_por_pagina.get(page_num, [])
    for img in page_imgs:
        img_x = img.get("x", 0)
        img_y = img["y"]
        coluna_img = "esquerda" if img_x < mid_x else "direita"
        el_img = {
            "tipo": "imagem",
            "y": img_y,
            "x": img_x,
            "largura": img.get("largura", 0),
            "arquivo": img["arquivo"],
            "pagina": page_num
        }
        if coluna_img == "esquerda":
            elementos_esquerda.append(el_img)
        else:
            elementos_direita.append(el_img)
            
    elementos_esquerda.sort(key=lambda x: x["y"])
    elementos_direita.sort(key=lambda x: x["y"])
    
    global_elements.extend(elementos_esquerda + elementos_direita)
    
# Rastrear o processamento na página 20
questao_atual = None
for idx_el, el in enumerate(global_elements):
    if el["tipo"] == "texto":
        match = re.search(r"QUESTÃO\s+(\d+)", el["texto"])
        if match:
            questao_atual = int(match.group(1))
    elif el["tipo"] == "imagem":
        if el["pagina"] == 20:
            print(f"\n[IMG Y={el['y']:.2f}, X={el['x']:.2f}] File={os.path.basename(el['arquivo'])}")
            print(f"  questao_atual ativa: {questao_atual}")
            q_alvo = questao_atual
            forcar_enunciado = False
            if questao_atual is not None:
                for next_el in global_elements[idx_el+1:]:
                    if next_el["tipo"] == "texto":
                        if next_el["pagina"] != el["pagina"]:
                            break
                        match_next = re.search(r"QUESTÃO\s+(\d+)", next_el["texto"])
                        if match_next:
                            dist_y = next_el["y"] - el["y"]
                            print(f"  Lookahead achou QUESTÃO {match_next.group(1)} em Y={next_el['y']:.2f}, dist_y={dist_y:.2f}")
                            if 0 < dist_y <= 50:
                                q_alvo = int(match_next.group(1))
                                forcar_enunciado = True
                                print(f"  Lookahead acionado! Reatribuído para {q_alvo}")
                            break
                        if next_el["y"] - el["y"] > 50:
                            break
            print(f"  Mapeando imagem para questão {q_alvo}")
            if q_alvo is not None and q_alvo in mapa_questoes:
                page = doc[20]
                mid_x = page.rect.width / 2
                labels_pagina = encontrar_labels_alternativas(page, mid_x)
                letra_mapped = map_image(el["y"], el["x"], mid_x, labels_pagina, img_w=el.get("largura", 0), page=page)
                print(f"  map_image retornou: {letra_mapped}")
