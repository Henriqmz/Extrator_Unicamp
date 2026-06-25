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

# Configurar dados mínimos semelhantes a test_runner.py
edital, ano, tipo_prova = detectar_edital_ano(PDF_PATH)
paginas, doc = extrair_pdf(PDF_PATH)
pasta_saida = os.path.join(BASE_DIR, "scratch", "temp_trace_mapping")
os.makedirs(pasta_saida, exist_ok=True)
prefixo_img = "debug_trace"
imagens = extrair_imagens(doc, output_dir=os.path.join(pasta_saida, "imgs"), prefixo=prefixo_img)
texto = extrair_texto(paginas, imagens)
questoes = extrair_questoes(texto, edital=edital, ano=ano, tipo_prova=tipo_prova)

print(f"Total de questões extraídas: {len(questoes)}")

# Agora vamos simular e tracejar o mapeamento de imagens
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
    
# Rastrear e imprimir detalhadamente na página index 6 (Página 7)
questao_atual = None
for el in global_elements:
    if el["tipo"] == "texto":
        match = re.search(r"QUESTÃO\s+(\d+)", el["texto"])
        if match:
            questao_atual = int(match.group(1))
            if el["pagina"] == 6:
                print(f"[PAGE 6 TEXT] Y={el['y']:.2f}: QUESTÃO {questao_atual}")
    elif el["tipo"] == "imagem":
        if el["pagina"] == 6:
            print(f"[PAGE 6 IMG] Y={el['y']:.2f}, X={el['x']:.2f}")
            q_alvo = questao_atual
            print(f"  questao_atual antes do lookahead: {questao_atual}")
            if questao_atual is not None:
                idx_el = global_elements.index(el)
                for next_el in global_elements[idx_el+1:]:
                    if next_el["tipo"] == "texto":
                        if next_el["pagina"] != el["pagina"]:
                            print(f"  Lookahead parou: nova página {next_el['pagina']}")
                            break
                        match_next = re.search(r"QUESTÃO\s+(\d+)", next_el["texto"])
                        if match_next:
                            dist_y = next_el["y"] - el["y"]
                            print(f"  Lookahead achou QUESTÃO {match_next.group(1)} em Y={next_el['y']:.2f}. dist_y={dist_y:.2f}")
                            if 0 < dist_y <= 50:
                                q_alvo = int(match_next.group(1))
                                print(f"  Reatribuído q_alvo = {q_alvo}")
                            break
                        if next_el["y"] - el["y"] > 50:
                            print(f"  Lookahead parou: dist_y > 50 em Y={next_el['y']:.2f}")
                            break
            print(f"  q_alvo final para mapeamento: {q_alvo}")
            if q_alvo in mapa_questoes:
                q_obj = mapa_questoes[q_alvo]
                page = doc[6]
                mid_x = page.rect.width / 2
                labels_pagina = encontrar_labels_alternativas(page, mid_x)
                letra_mapped = map_image(el["y"], el["x"], mid_x, labels_pagina, img_w=el.get("largura", 0), page=page)
                print(f"  letra_mapped por map_image: {letra_mapped}")
                img_caminho = f"{IMG_REL_PREFIX}{os.path.basename(el['arquivo'])}"
                print(f"  Caminho da imagem: {img_caminho}")
                
# Verificando q18 ao final
q18 = mapa_questoes.get(18)
if q18:
    print(f"\nQ18 url_img final: {q18.conteudo.url_img}")
    print(f"Q18 alternativas:")
    for l in "abcd":
        alt = getattr(q18.alternativas, l)
        print(f"  {l}: url_img={alt.url_img if alt else None}")
