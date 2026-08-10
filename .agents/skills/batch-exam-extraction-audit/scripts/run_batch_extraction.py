import os
import sys
import json
import glob

sys.stdout.reconfigure(encoding='utf-8')

# Adiciona o diretório do projeto ao sys.path
projeto_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.append(projeto_root)

from extractor import extrair_pdf, extrair_imagens, extrair_texto
from processor import (
    detectar_edital_ano,
    extrair_questoes,
    extrair_questoes_dissertativas,
    extrair_textos_comp,
    mapear_textos_comp,
    enriquecer,
    mapear_imagens_a_questoes_e_alternativas,
    extrair_gabarito,
    aplicar_gabarito
)
from saver import salvar_questoes, salvar_textos

output_base = os.path.join(projeto_root, "exec_results")
os.makedirs(output_base, exist_ok=True)

def buscar_pdf_por_padrao(subpath_pattern):
    base_provas = os.path.join(projeto_root, "Provas")
    matches = glob.glob(os.path.join(base_provas, "**", subpath_pattern), recursive=True)
    if matches:
        return matches[0]
    return None

provas_info = [
    # 2022
    {"nome": "2022_1fase_Q-X", "pdf": buscar_pdf_por_padrao("*prova-q-x.pdf"), "gabarito": buscar_pdf_por_padrao("*gabarito-q-x.pdf"), "tipo": "objetiva"},
    {"nome": "2022_2fase_Biologicas", "pdf": buscar_pdf_por_padrao("*prova-ciencias-biologicas-saude.pdf"), "gabarito": None, "tipo": "dissertativa"},
    {"nome": "2022_2fase_Exatas", "pdf": buscar_pdf_por_padrao("*prova-exatas-tecnologicas.pdf"), "gabarito": None, "tipo": "dissertativa"},
    {"nome": "2022_2fase_Humanas", "pdf": buscar_pdf_por_padrao("*prova-humanas-artes.pdf"), "gabarito": None, "tipo": "dissertativa"},
    {"nome": "2022_2fase_Redacao", "pdf": buscar_pdf_por_padrao("*prova-redacao-portugues-inter-ingles.pdf"), "gabarito": None, "tipo": "dissertativa"},
    # 2023
    {"nome": "2023_1fase_Q-Z", "pdf": buscar_pdf_por_padrao("*provas-unicamp-2023-q-e-z.pdf"), "gabarito": None, "tipo": "objetiva"},
    {"nome": "2023_2fase_Biologicas", "pdf": buscar_pdf_por_padrao("*prova-ciencias-biologias-saude-unicamp-2023-fase-2.pdf"), "gabarito": None, "tipo": "dissertativa"},
    {"nome": "2023_2fase_Exatas", "pdf": buscar_pdf_por_padrao("*prova-ciencias-exatas-unicamp-2023-fase-2.pdf"), "gabarito": None, "tipo": "dissertativa"},
    {"nome": "2023_2fase_Humanas", "pdf": buscar_pdf_por_padrao("*prova-ciencias-humanas-artes-unicamp-2023-fase-2.pdf"), "gabarito": None, "tipo": "dissertativa"},
    {"nome": "2023_2fase_Redacao", "pdf": buscar_pdf_por_padrao("*prova-redacao-portugues-literaturas-unicamp-2023-fase-2.pdf"), "gabarito": None, "tipo": "dissertativa"},
    # 2024
    {"nome": "2024_1fase_Q-Y", "pdf": buscar_pdf_por_padrao("*provas-q-y-unicamp-1-fase-2024.pdf"), "gabarito": None, "tipo": "objetiva"},
    # 2025
    {"nome": "2025_1fase_Q-Z", "pdf": buscar_pdf_por_padrao("*prova-q-z-1-fase-unicamp-2025.pdf"), "gabarito": None, "tipo": "objetiva"},
    # 2026
    {"nome": "2026_1fase_Q-X", "pdf": buscar_pdf_por_padrao("*prova-q-x-1-fase-unicamp-2026.pdf"), "gabarito": None, "tipo": "objetiva"},
    {"nome": "2026_2fase_Dia1", "pdf": buscar_pdf_por_padrao("*unicamp-2026-2-fase-prova-dia-1.pdf"), "gabarito": None, "tipo": "dissertativa"}
]

resumo = []

for item in provas_info:
    nome = item["nome"]
    pdf_path = item["pdf"]
    gabarito_path = item["gabarito"]
    tipo_proc = item["tipo"]

    if not pdf_path or not os.path.exists(pdf_path):
        print(f"⚠️ PDF não encontrado para {nome}")
        continue

    pasta_saida = os.path.join(output_base, nome)
    imgs_dir = os.path.join(pasta_saida, "imgs")
    os.makedirs(pasta_saida, exist_ok=True)
    os.makedirs(imgs_dir, exist_ok=True)

    print(f"\n==========================================")
    print(f"▶ Processando {nome} ({tipo_proc})...")

    edital, ano, tipo_prova = detectar_edital_ano(pdf_path)
    paginas, doc = extrair_pdf(pdf_path)

    prefixo_img = f"{edital}_{ano}_{tipo_prova.replace('/', '-')}"
    imagens = extrair_imagens(doc, output_dir=imgs_dir, prefixo=prefixo_img)
    texto = extrair_texto(paginas, imagens)

    textos_comp = extrair_textos_comp(texto)
    mapa_textos = mapear_textos_comp(textos_comp)

    if tipo_proc == "objetiva":
        questoes = extrair_questoes(texto, edital=edital, ano=ano, tipo_prova=tipo_prova)
    else:
        questoes = extrair_questoes_dissertativas(texto, edital=edital, ano=ano, tipo_prova=tipo_prova)

    questoes = enriquecer(questoes, mapa_textos, {})
    mapear_imagens_a_questoes_e_alternativas(questoes, imagens, doc)

    if gabarito_path and os.path.exists(gabarito_path):
        res = extrair_gabarito(gabarito_path)
        if isinstance(res, tuple):
            questoes = aplicar_gabarito(questoes, res[0])
        elif isinstance(res, list):
            questoes = aplicar_gabarito(questoes, res[0][0])

    salvar_questoes(questoes, pasta=pasta_saida)
    if textos_comp:
        salvar_textos(textos_comp, pasta=pasta_saida, edital=edital, ano=ano, tipo_ou_cor=tipo_prova)

    total_imgs = len(glob.glob(os.path.join(imgs_dir, "*.webp")))
    total_q = len(questoes)
    num_q_com_img = sum(1 for q in questoes if (q.conteudo.url_img or (q.alternativas and any(alt and alt.url_img for alt in [q.alternativas.a, q.alternativas.b, q.alternativas.c, q.alternativas.d, q.alternativas.e] if alt))))

    info_dict = {
        "nome": nome,
        "ano": ano,
        "tipo": tipo_proc,
        "total_questoes": total_q,
        "total_imagens_extraidas": total_imgs,
        "questoes_com_imagem": num_q_com_img,
        "pasta": pasta_saida
    }
    resumo.append(info_dict)
    print(f"✔ {nome}: {total_q} questões extraídas, {total_imgs} imagens em disco, {num_q_com_img} questões com imagem vinculada.")

resumo_path = os.path.join(output_base, "resumo_execucao.json")
with open(resumo_path, "w", encoding="utf-8") as f:
    json.dump(resumo, f, indent=2, ensure_ascii=False)

print(f"\n✅ Execução em lote finalizada! Resumo salvo em {resumo_path}")
