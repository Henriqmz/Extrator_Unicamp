import os
import sys
import re
import json
import shutil
import fitz
import pytest
from PIL import Image
from extractor import *
from processor import *
from saver import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PDF_PATH = os.path.join(BASE_DIR, "Provas", "provas-e-gabaritos-unicamp-2026", "1-fase-unicamp-2026", "prova-q-x-1-fase-unicamp-2026.pdf")
GABARITO_PATH = os.path.join(BASE_DIR, "Provas", "provas-e-gabaritos-unicamp-2026", "1-fase-unicamp-2026", "gabarito-q-x-1-fase-unicamp-2026.pdf")
PDF_2FASE_2026_PATH = os.path.join(BASE_DIR, "Provas", "provas-e-gabaritos-unicamp-2026", "2-fase-unicamp-2026", "unicamp-2026-2-fase-prova-dia-1.pdf")

PDF_2021_PATH = os.path.join(BASE_DIR, "Provas", "1-provas-e-gabaritos-unicamp-2021", "1ª fase", "Provas E e G.pdf")
GABARITO_2021_PATH = os.path.join(BASE_DIR, "Provas", "1-provas-e-gabaritos-unicamp-2021", "1ª fase", "DIA1_gabarito_2021.pdf")

PDF_2022_PATH = os.path.join(BASE_DIR, "Provas", "2-provas-e-gabaritos-unicamp-2022", "Primeira fase", "prova-q-x.pdf")
GABARITO_2022_PATH = os.path.join(BASE_DIR, "Provas", "2-provas-e-gabaritos-unicamp-2022", "Primeira fase", "gabarito-1-fase.pdf")

PDF_2023_QZ_PATH = os.path.join(BASE_DIR, "Provas", "1-provas-e-gabaritos-unicamp-2023", "provas-gabaritos-vestibular-unicamp-2023", "1º Fase", "provas-unicamp-2023-q-e-z.pdf")
PDF_2023_RY_PATH = os.path.join(BASE_DIR, "Provas", "1-provas-e-gabaritos-unicamp-2023", "provas-gabaritos-vestibular-unicamp-2023", "1º Fase", "provas-unicamp-2023-r-e-y.pdf")
GABARITO_2023_PATH = os.path.join(BASE_DIR, "Provas", "1-provas-e-gabaritos-unicamp-2023", "provas-gabaritos-vestibular-unicamp-2023", "1º Fase", "gabaritos-1-fase-vestibular-2023-unicamp.pdf")

PDF_2024_QY_PATH = os.path.join(BASE_DIR, "Provas", "provas-e-gabaritos-unicamp-2024", "provas-e-gabaritos-unicamp-2024", "provas-q-y-unicamp-1-fase-2024.pdf")
GABARITO_2024_PY_PATH = os.path.join(BASE_DIR, "Provas", "provas-e-gabaritos-unicamp-2024", "provas-e-gabaritos-unicamp-2024", "gabarito-p-y-unicamp-2024.pdf")

PDF_2025_PATH = os.path.join(BASE_DIR, "Provas", "2-provas-e-gabaritos-unicamp-2025", "provas-e-gabaritos-unicamp-2025", "provas-e-gabaritos-unicamp-vestibular-2025", "1-fase-provas-gabaritos-unicamp-vestibular-2025", "prova-q-z-1-fase-unicamp-2025.pdf")
GABARITO_2025_PATH = os.path.join(BASE_DIR, "Provas", "2-provas-e-gabaritos-unicamp-2025", "provas-e-gabaritos-unicamp-2025", "provas-e-gabaritos-unicamp-vestibular-2025", "1-fase-provas-gabaritos-unicamp-vestibular-2025", "gabarito-q-z-1-fase-unicamp-2025.pdf")

def _run_setup(pdf_path, gabarito_path=None, choose_caderno_name=None, fase=1):
    carregar_env()
    assert os.path.exists(pdf_path), f"PDF não encontrado: {pdf_path}"
    edital, ano, tipo_prova = detectar_edital_ano(pdf_path)
    paginas, doc = extrair_pdf(pdf_path)
    pasta_saida = os.path.join(BASE_DIR, f"{edital}_{ano}_pytest_{tipo_prova.replace('/', '-')}")
    if fase == 2:
        pasta_saida += "_2fase"
    if os.path.exists(pasta_saida):
        shutil.rmtree(pasta_saida)
    prefixo_img = f"{edital}_{ano}_{tipo_prova.replace('/', '-')}"
    if fase == 2:
        prefixo_img += "_2fase"
    imagens = extrair_imagens(doc, output_dir=os.path.join(pasta_saida, "imgs"), prefixo=prefixo_img)
    texto = extrair_texto(paginas, imagens)
    textos_comp = extrair_textos_comp(texto)
    if fase == 1:
        questoes = extrair_questoes(texto, edital=edital, ano=ano, tipo_prova=tipo_prova)
    else:
        questoes = extrair_questoes_dissertativas(texto, edital=edital, ano=ano, tipo_prova=tipo_prova)
    mapa_textos = mapear_textos_comp(textos_comp)
    questoes = enriquecer(questoes, mapa_textos, {})
    mapear_imagens_a_questoes_e_alternativas(questoes, imagens, doc)
    if gabarito_path and os.path.exists(gabarito_path):
        res = extrair_gabarito(gabarito_path)
        if isinstance(res, list):
            gabarito_respostas = None
            if choose_caderno_name:
                keys = [k.strip().lower() for k in re.findall(r'[a-zA-Z]', choose_caderno_name) if k.lower() != 'e']
                for respostas, tipo in res:
                    if any(k in tipo.lower() for k in keys):
                        gabarito_respostas = respostas
                        break
            if not gabarito_respostas:
                gabarito_respostas = res[0][0]
            questoes = aplicar_gabarito(questoes, gabarito_respostas)
        elif isinstance(res, tuple):
            respostas, tipo = res
            questoes = aplicar_gabarito(questoes, respostas)
    salvar_questoes(questoes, pasta=pasta_saida)
    salvar_textos(textos_comp, pasta=pasta_saida, edital=edital, ano=ano, tipo_ou_cor=tipo_prova)
    return {
        "edital": edital, "ano": ano, "tipo_prova": tipo_prova, "paginas": paginas,
        "questoes": questoes, "textos_comp": textos_comp, "imagens": imagens,
        "pasta_saida": pasta_saida, "doc": doc
    }

@pytest.fixture(scope="session")
def data_2026():
    return _run_setup(PDF_PATH, GABARITO_PATH)

@pytest.fixture(scope="session")
def data_2026_2fase():
    return _run_setup(PDF_2FASE_2026_PATH, fase=2)

@pytest.fixture(scope="session")
def data_2021():
    return _run_setup(PDF_2021_PATH, GABARITO_2021_PATH, choose_caderno_name="E e G")

@pytest.fixture(scope="session")
def data_2022():
    return _run_setup(PDF_2022_PATH, GABARITO_2022_PATH)

@pytest.fixture(scope="session")
def data_2023_qz():
    return _run_setup(PDF_2023_QZ_PATH, GABARITO_2023_PATH, choose_caderno_name="Q e Z")

@pytest.fixture(scope="session")
def data_2023_ry():
    return _run_setup(PDF_2023_RY_PATH, GABARITO_2023_PATH, choose_caderno_name="R e Y")

@pytest.fixture(scope="session")
def data_2024_qy():
    return _run_setup(PDF_2024_QY_PATH, GABARITO_2024_PY_PATH, choose_caderno_name="Q e Y")

@pytest.fixture(scope="session")
def data_2025():
    return _run_setup(PDF_2025_PATH, GABARITO_2025_PATH, choose_caderno_name="Q e Z")

# ================= 2026 TESTS =================
def test_r01_deteccao_edital_ano_tipo_2026(data_2026):
    assert data_2026["edital"] == "unicamp"
    assert data_2026["ano"] == 2026
    assert data_2026["tipo_prova"] == "Q-X"

def test_r02_total_paginas_2026(data_2026):
    assert len(data_2026["paginas"]) == 27

def test_r03_total_questoes_2026(data_2026):
    assert len(data_2026["questoes"]) == 72

def test_r04_total_textos_comp_2026(data_2026):
    assert len(data_2026["textos_comp"]) == 3

def test_r05_questao_1_tem_imagens_2026(data_2026):
    q1 = next(q for q in data_2026["questoes"] if q.metadados.numero == 1)
    assert len(q1.conteudo.url_img) >= 1

def test_r06_questao_2_imagem_grupo_2026(data_2026):
    q2 = next(q for q in data_2026["questoes"] if q.metadados.numero == 2)
    assert len(q2.conteudo.url_img) == 1
    assert "img_1" in q2.conteudo.url_img[0]

def test_r07_gabarito_q46_correta_2026(data_2026):
    q46 = next(q for q in data_2026["questoes"] if q.metadados.numero == 46)
    assert q46.alternativas.c.correta is True

def test_r08_gabarito_q46_incorretas_2026(data_2026):
    q46 = next(q for q in data_2026["questoes"] if q.metadados.numero == 46)
    assert q46.alternativas.a.correta is False
    assert q46.alternativas.b.correta is False
    assert q46.alternativas.d.correta is False

def test_r09_questoes_salvas_json_2026(data_2026):
    arquivos_json = [f for f in os.listdir(data_2026["pasta_saida"]) if f.endswith(".json") and "COMP" not in f]
    assert len(arquivos_json) == 72

def test_r10_textos_comp_salvos_json_2026(data_2026):
    arquivos_comp = [f for f in os.listdir(data_2026["pasta_saida"]) if "COMP" in f]
    assert len(arquivos_comp) == 3

def test_r11_schema_json_q1_2026(data_2026):
    nome_q1 = f"{data_2026['edital']}_{data_2026['ano']}_{data_2026['tipo_prova'].replace('/', '-')}_1.json"
    with open(os.path.join(data_2026["pasta_saida"], nome_q1), "r", encoding="utf-8") as f:
        js = json.load(f)
        conteudo = js["conteudo"]
        assert "enunciado" in conteudo
        assert "url_img" in conteudo
        assert "dificuldade" in conteudo
        assert "resolucao" in conteudo
        assert "dica" in conteudo
        assert "objetiva" in conteudo
        assert conteudo["objetiva"] is True
        especificacao = js["especificacao"]
        assert "area" not in especificacao
        assert "disciplina" in especificacao
        assert "assunto" in especificacao
        assert "topico" in especificacao
        assert isinstance(especificacao["disciplina"], list)
        assert isinstance(especificacao["assunto"], list)
        assert isinstance(especificacao["topico"], list)

def test_r12_dica_lista_ou_none_2026(data_2026):
    q1 = next(q for q in data_2026["questoes"] if q.metadados.numero == 1)
    assert q1.conteudo.dica is None or isinstance(q1.conteudo.dica, list)

def test_n01_q66_imagem_grupo(data_2026):
    q66 = next(q for q in data_2026["questoes"] if q.metadados.numero == 66)
    assert len(q66.conteudo.url_img) >= 1
    assert any("img_1" in img for img in q66.conteudo.url_img)

def test_n02_q66_sem_imagens_individuais(data_2026):
    q66 = next(q for q in data_2026["questoes"] if q.metadados.numero == 66)
    for img in q66.conteudo.url_img:
        assert "img_" in img

def test_n03_todas_imagens_webp(data_2026):
    imgs_dir = os.path.join(data_2026["pasta_saida"], "imgs")
    arquivos = os.listdir(imgs_dir)
    assert len(arquivos) > 0
    for f in arquivos:
        assert f.endswith(".webp")

def test_n04_json_q1_campo_dificuldade(data_2026):
    nome_q1 = f"{data_2026['edital']}_{data_2026['ano']}_{data_2026['tipo_prova'].replace('/', '-')}_1.json"
    with open(os.path.join(data_2026["pasta_saida"], nome_q1), "r", encoding="utf-8") as f:
        js = json.load(f)
        assert "dificuldade" in js["conteudo"]

def test_n05_campo_dificuldade_null_inicial(data_2026):
    nome_q1 = f"{data_2026['edital']}_{data_2026['ano']}_{data_2026['tipo_prova'].replace('/', '-')}_1.json"
    with open(os.path.join(data_2026["pasta_saida"], nome_q1), "r", encoding="utf-8") as f:
        js = json.load(f)
        assert js["conteudo"]["dificuldade"] is None

def test_n06_gabarito_2021_multiplos_tipos():
    assert os.path.exists(GABARITO_2021_PATH)
    res = extrair_gabarito(GABARITO_2021_PATH)
    assert isinstance(res, list)
    assert len(res) >= 2

def test_n07_gabarito_2026_tipo_unico():
    res = extrair_gabarito(GABARITO_PATH)
    assert isinstance(res, tuple)
    assert len(res) == 2
    assert isinstance(res[0], dict)
    assert isinstance(res[1], str)

# ================= 2021 TESTS =================
def test_e01_deteccao_edital_ano_tipo_2021(data_2021):
    assert data_2021["edital"] == "unicamp"
    assert data_2021["ano"] == 2021
    assert data_2021["tipo_prova"] == "E-G"

def test_e02_q10_sem_drawing_texto_como_imagem(data_2021):
    q10 = next(q for q in data_2021["questoes"] if q.metadados.numero == 10)
    assert not any("drawing" in img for img in q10.conteudo.url_img)

def test_e03_q10_enunciado_contem_texto_cronica(data_2021):
    q10 = next(q for q in data_2021["questoes"] if q.metadados.numero == 10)
    assert "desigualdade" in q10.conteudo.enunciado.lower()

def test_e04_q20_imagens_individuais_alternativas(data_2021):
    q20 = next(q for q in data_2021["questoes"] if q.metadados.numero == 20)
    assert len(q20.alternativas.a.url_img) == 1
    assert len(q20.alternativas.b.url_img) == 1
    assert len(q20.alternativas.c.url_img) == 1
    assert len(q20.alternativas.d.url_img) == 1

def test_e05_q23_imagens_individuais_alternativas(data_2021):
    q23 = next(q for q in data_2021["questoes"] if q.metadados.numero == 23)
    assert len(q23.alternativas.a.url_img) == 1
    assert len(q23.alternativas.b.url_img) == 1
    assert len(q23.alternativas.c.url_img) == 1
    assert len(q23.alternativas.d.url_img) == 1

def test_e06_q41_imagens_triangulos_distribuidas(data_2021):
    q41 = next(q for q in data_2021["questoes"] if q.metadados.numero == 41)
    assert len(q41.alternativas.a.url_img) == 3
    assert len(q41.alternativas.b.url_img) == 3
    assert len(q41.alternativas.c.url_img) == 3
    assert len(q41.alternativas.d.url_img) == 3

def test_e07_q55_sem_duplicacao_enunciado(data_2021):
    q55 = next(q for q in data_2021["questoes"] if q.metadados.numero == 55)
    assert len(q55.conteudo.enunciado) < 1500

def test_e08_q68_largura_agrupamento(data_2021):
    for img_dict in data_2021["imagens"]:
        if img_dict.get("grupo") or "group" in os.path.basename(img_dict["arquivo"]):
            with Image.open(img_dict["arquivo"]) as img:
                largura_real = img.width / 2
                assert largura_real <= 595.2 * 0.61

def test_e09_associacao_imagens_q70_q71(data_2021):
    q70 = next(q for q in data_2021["questoes"] if q.metadados.numero == 70)
    for img_rel in q70.conteudo.url_img:
        basename = os.path.basename(img_rel)
        img_dict = next((x for x in data_2021["imagens"] if os.path.basename(x["arquivo"]) == basename), None)
        assert img_dict is not None
        assert img_dict["pagina"] in [19, 20]

def test_e10_drawing_eh_texto(data_2021):
    page_4 = data_2021["doc"][4]
    rect_cronica = fitz.Rect(314, 87, 568, 429)
    assert drawing_eh_texto(page_4, rect_cronica) is True

def test_e11_coluna_classificacao():
    mid_x = 298
    r_leve = fitz.Rect(296, 100, 310, 200)
    assert coluna(r_leve, mid_x) == "D"

def test_e12_detectar_padrao_alternativas():
    mid_x = 298
    elementos = [
        {"tipo": "raster", "rect": fitz.Rect(30, 100, 130, 180)},
        {"tipo": "raster", "rect": fitz.Rect(30, 200, 130, 280)},
        {"tipo": "raster", "rect": fitz.Rect(30, 300, 130, 380)}
    ]
    indices = detectar_padrao_alternativas(elementos, mid_x)
    assert len(indices) == 3

def test_e13_split_alternativas_limpo(data_2021):
    q20 = next(q for q in data_2021["questoes"] if q.metadados.numero == 20)
    assert "b)" not in q20.alternativas.a.texto

# ================= BUGFIX TESTS =================
def test_f01_dimensao_minima_imagens_2021(data_2021):
    for img in data_2021["imagens"]:
        with Image.open(img["arquivo"]) as p_img:
            assert p_img.width >= 10 and p_img.height >= 10

def test_f02_total_imagens_2021_razoavel(data_2021):
    assert len(data_2021["imagens"]) <= 150

def test_f03_q71_tem_imagem_enunciado(data_2021):
    q71 = next(q for q in data_2021["questoes"] if q.metadados.numero == 71)
    assert len(q71.conteudo.url_img) >= 1

def test_f04_q70_tem_imagem_enunciado(data_2021):
    q70 = next(q for q in data_2021["questoes"] if q.metadados.numero == 70)
    assert len(q70.conteudo.url_img) >= 1

def test_f05_2023_qz_tipo(data_2023_qz):
    assert data_2023_qz["tipo_prova"] == "Q-Z"

def test_f06_2023_ry_tipo(data_2023_ry):
    assert data_2023_ry["tipo_prova"] == "R-Y"

def test_f07_gabarito_2025_respostas(data_2025):
    assert len(data_2025["questoes"]) == 72
    respostas_corretas = []
    for q in data_2025["questoes"]:
        for l in ["a", "b", "c", "d", "e"]:
            alt = getattr(q.alternativas, l)
            if alt and alt.correta:
                respostas_corretas.append(q.metadados.numero)
                break
    assert len(respostas_corretas) == 71

def test_f08_gabarito_2021_sem_newline():
    res = extrair_gabarito(GABARITO_2021_PATH)
    for _, tipo in res:
        assert "\n" not in tipo

def test_f09_arquivos_imagem_integros(data_2026, data_2021, data_2022, data_2023_qz, data_2024_qy, data_2025):
    for dataset in [data_2026, data_2021, data_2022, data_2023_qz, data_2024_qy, data_2025]:
        for img in dataset["imagens"]:
            caminho = img["arquivo"]
            if os.path.exists(caminho):
                assert os.path.getsize(caminho) > 50

def test_f10_2024_qy_alternativas_q67(data_2024_qy):
    q67 = next(q for q in data_2024_qy["questoes"] if q.metadados.numero == 67)
    assert len(q67.alternativas.a.url_img) == 1
    assert len(q67.alternativas.b.url_img) == 1
    assert len(q67.alternativas.c.url_img) == 1
    assert len(q67.alternativas.d.url_img) == 1

# ================= UNIT TESTS =================
def test_u01_drawing_eh_texto_denso(data_2021):
    page_4 = data_2021["doc"][4]
    rect = fitz.Rect(314, 87, 568, 429)
    assert drawing_eh_texto(page_4, rect) is True

def test_u02_drawing_eh_texto_grafico(data_2021):
    page_8 = data_2021["doc"][8]
    rect = fitz.Rect(41.2, 411.2, 136.0, 497.2)
    assert drawing_eh_texto(page_8, rect) is False

def test_u03_coluna_esquerda_puro():
    r = fitz.Rect(20, 100, 250, 200)
    assert coluna(r, 298) == "E"

def test_u04_coluna_direita_puro():
    r = fitz.Rect(320, 100, 550, 200)
    assert coluna(r, 298) == "D"

def test_u05_coluna_centro_cruzando_significativo():
    r = fitz.Rect(100, 100, 500, 200)
    assert coluna(r, 298) == "C"

def test_u06_coluna_centro_cruzando_marginal():
    r_marginal = fitz.Rect(296, 100, 350, 200)
    assert coluna(r_marginal, 298) == "D"

def test_u07_detectar_padrao_3_imagens():
    elementos = [
        {"tipo": "raster", "rect": fitz.Rect(30, 100, 130, 180)},
        {"tipo": "raster", "rect": fitz.Rect(30, 200, 130, 280)},
        {"tipo": "raster", "rect": fitz.Rect(30, 300, 130, 380)}
    ]
    assert len(detectar_padrao_alternativas(elementos, 298)) == 3

def test_u08_detectar_padrao_2_imagens():
    elementos = [
        {"tipo": "raster", "rect": fitz.Rect(30, 100, 130, 180)},
        {"tipo": "raster", "rect": fitz.Rect(30, 200, 130, 280)}
    ]
    assert len(detectar_padrao_alternativas(elementos, 298)) == 0

# ================= CORRETUDE DE LAYOUT =================
def test_t01_horiz_2022(data_2022):
    q22 = next(q for q in data_2022["questoes"] if q.metadados.numero == 22)
    assert q22.alternativas.c is not None and q22.alternativas.c.texto
    assert q22.alternativas.d is not None and q22.alternativas.d.texto

def test_t02_horiz_2024(data_2024_qy):
    q65 = next(q for q in data_2024_qy["questoes"] if q.metadados.numero == 65)
    assert all(getattr(q65.alternativas, letra) and getattr(q65.alternativas, letra).texto for letra in "abcd")

def test_t03_fisica_2021(data_2021):
    for num in range(33, 41):
        q = next(q for q in data_2021["questoes"] if q.metadados.numero == num)
        assert all(getattr(q.alternativas, letra) and getattr(q.alternativas, letra).texto for letra in "abcd")

def test_t04_img_map_2026_zuzu_angel(data_2026):
    q33 = next(q for q in data_2026["questoes"] if q.metadados.numero == 33)
    assert q33.alternativas.c is not None and q33.alternativas.c.texto
    q34 = next(q for q in data_2026["questoes"] if q.metadados.numero == 34)
    assert len(q34.conteudo.enunciado.strip()) > 50

def test_t05_img_map_2021_cartaz_oms(data_2021):
    q18 = next(q for q in data_2021["questoes"] if q.metadados.numero == 18)
    assert len(q18.conteudo.url_img) == 1

# ================= 2026 2ª FASE =================
def test_d01_2026_2fase_quantidade(data_2026_2fase):
    assert len(data_2026_2fase["questoes"]) == 10

def test_d02_2026_2fase_estrutura_q1(data_2026_2fase):
    q1 = next(q for q in data_2026_2fase["questoes"] if q.metadados.numero == 1)
    assert q1.alternativas is None
    assert "a)" in q1.conteudo.enunciado
    assert "b)" in q1.conteudo.enunciado
    assert "mecanismo linguístico" in q1.conteudo.enunciado.lower()
