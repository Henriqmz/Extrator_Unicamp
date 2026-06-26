import os
import sys
import re
import json
import shutil
import fitz
from PIL import Image
from extractor import *
from processor import *
from saver import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2026
PDF_PATH = os.path.join(BASE_DIR, "Provas", "provas-e-gabaritos-unicamp-2026", "1-fase-unicamp-2026", "prova-q-x-1-fase-unicamp-2026.pdf")
GABARITO_PATH = os.path.join(BASE_DIR, "Provas", "provas-e-gabaritos-unicamp-2026", "1-fase-unicamp-2026", "gabarito-q-x-1-fase-unicamp-2026.pdf")
PDF_2FASE_2026_PATH = os.path.join(BASE_DIR, "Provas", "provas-e-gabaritos-unicamp-2026", "2-fase-unicamp-2026", "unicamp-2026-2-fase-prova-dia-1.pdf")

# 2021
PDF_2021_PATH = os.path.join(BASE_DIR, "Provas", "1-provas-e-gabaritos-unicamp-2021", "1ª fase", "Provas E e G.pdf")
GABARITO_2021_PATH = os.path.join(BASE_DIR, "Provas", "1-provas-e-gabaritos-unicamp-2021", "1ª fase", "DIA1_gabarito_2021.pdf")

# 2022
PDF_2022_PATH = os.path.join(BASE_DIR, "Provas", "2-provas-e-gabaritos-unicamp-2022", "Primeira fase", "prova-q-x.pdf")
GABARITO_2022_PATH = os.path.join(BASE_DIR, "Provas", "2-provas-e-gabaritos-unicamp-2022", "Primeira fase", "gabarito-1-fase.pdf")

# 2023
PDF_2023_QZ_PATH = os.path.join(BASE_DIR, "Provas", "1-provas-e-gabaritos-unicamp-2023", "provas-gabaritos-vestibular-unicamp-2023", "1º Fase", "provas-unicamp-2023-q-e-z.pdf")
PDF_2023_RY_PATH = os.path.join(BASE_DIR, "Provas", "1-provas-e-gabaritos-unicamp-2023", "provas-gabaritos-vestibular-unicamp-2023", "1º Fase", "provas-unicamp-2023-r-e-y.pdf")
GABARITO_2023_PATH = os.path.join(BASE_DIR, "Provas", "1-provas-e-gabaritos-unicamp-2023", "provas-gabaritos-vestibular-unicamp-2023", "1º Fase", "gabaritos-1-fase-vestibular-2023-unicamp.pdf")

# 2024
PDF_2024_QY_PATH = os.path.join(BASE_DIR, "Provas", "provas-e-gabaritos-unicamp-2024", "provas-e-gabaritos-unicamp-2024", "provas-q-y-unicamp-1-fase-2024.pdf")
GABARITO_2024_PY_PATH = os.path.join(BASE_DIR, "Provas", "provas-e-gabaritos-unicamp-2024", "provas-e-gabaritos-unicamp-2024", "gabarito-p-y-unicamp-2024.pdf")

# 2025
PDF_2025_PATH = os.path.join(BASE_DIR, "Provas", "2-provas-e-gabaritos-unicamp-2025", "provas-e-gabaritos-unicamp-2025", "provas-e-gabaritos-unicamp-vestibular-2025", "1-fase-provas-gabaritos-unicamp-vestibular-2025", "prova-q-z-1-fase-unicamp-2025.pdf")
GABARITO_2025_PATH = os.path.join(BASE_DIR, "Provas", "2-provas-e-gabaritos-unicamp-2025", "provas-e-gabaritos-unicamp-2025", "provas-e-gabaritos-unicamp-vestibular-2025", "1-fase-provas-gabaritos-unicamp-vestibular-2025", "gabarito-q-z-1-fase-unicamp-2025.pdf")


class TestSuite:
    def __init__(self):
        self.passes = 0
        self.fails = 0
        self.total = 0
        self.failures_list = []

    def run(self, test_id, desc, test_fn):
        self.total += 1
        print(f"Executando {test_id} - {desc} ... ", end="")
        sys.stdout.flush()
        try:
            test_fn()
            self.passes += 1
            print("PASS")
        except Exception as e:
            self.fails += 1
            print("FAIL")
            print(f"    Erro: {e}")
            self.failures_list.append((test_id, desc, str(e)))

    def report(self):
        print("\n" + "="*40)
        print(f" +------------------------------+")
        print(f" |  RESULTADO: {self.passes}/{self.total} PASS        |")
        print(f" |  FALHAS:    {self.fails}                |")
        print(f" +------------------------------+")
        print("" + "="*40)
        if self.fails > 0:
            print("\nDetalhes das Falhas:")
            for tid, desc, err in self.failures_list:
                print(f"  [{tid}] {desc}: {err}")
            sys.exit(1)
        else:
            print(f"\nTodos os {self.total} testes passaram com sucesso! (Código de saída: 0)")
            sys.exit(0)


def run_setup_for_pdf(pdf_path, gabarito_path=None, choose_caderno_name=None, enrich_ia=False, fase=1):
    """
    Roda o pipeline completo (sem IA por padrão) para um PDF específico.
    """
    carregar_env()
    if not os.path.exists(pdf_path):
        print(f"Erro: PDF não encontrado em {pdf_path}")
        sys.exit(1)
        
    edital, ano, tipo_prova = detectar_edital_ano(pdf_path)
    paginas, doc = extrair_pdf(pdf_path)
    
    pasta_saida = os.path.join(BASE_DIR, f"{edital}_{ano}_test_{tipo_prova.replace('/', '-')}")
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
            # Múltiplos gabaritos no mesmo PDF. Encontrar o correspondente.
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
            
    if enrich_ia:
        api_key = os.getenv("GEMINI_API_KEY")
        questoes = enriquecer_questoes_com_ia(questoes, api_key, mapa_textos=mapa_textos, max_questoes=2)
        
    salvar_questoes(questoes, pasta=pasta_saida)
    salvar_textos(textos_comp, pasta=pasta_saida, edital=edital, ano=ano, tipo_ou_cor=tipo_prova)
    
    return {
        "edital": edital,
        "ano": ano,
        "tipo_prova": tipo_prova,
        "paginas": paginas,
        "questoes": questoes,
        "textos_comp": textos_comp,
        "imagens": imagens,
        "pasta_saida": pasta_saida,
        "doc": doc
    }


def main():
    print("Iniciando setups de teste para múltiplos anos (2021-2026)...")
    
    # 2026 (desativado enriquecimento por IA conforme solicitação)
    data_2026 = run_setup_for_pdf(PDF_PATH, GABARITO_PATH, enrich_ia=False)
    
    # 2026 Segunda Fase
    data_2026_2fase = run_setup_for_pdf(PDF_2FASE_2026_PATH, fase=2)
    
    # 2021
    data_2021 = run_setup_for_pdf(PDF_2021_PATH, GABARITO_2021_PATH, choose_caderno_name="E e G")
    
    # 2022
    data_2022 = run_setup_for_pdf(PDF_2022_PATH, GABARITO_2022_PATH)
    
    # 2023 Q-Z e R-Y
    data_2023_qz = run_setup_for_pdf(PDF_2023_QZ_PATH, GABARITO_2023_PATH, choose_caderno_name="Q e Z")
    data_2023_ry = run_setup_for_pdf(PDF_2023_RY_PATH, GABARITO_2023_PATH, choose_caderno_name="R e Y")
    
    # 2024 Q-Y
    data_2024_qy = run_setup_for_pdf(PDF_2024_QY_PATH, GABARITO_2024_PY_PATH, choose_caderno_name="Q e Y")
    
    # 2025 Q-Z
    data_2025 = run_setup_for_pdf(PDF_2025_PATH, GABARITO_2025_PATH, choose_caderno_name="Q e Z")
    
    suite = TestSuite()

    # ================= 2026 TESTS (R01 - R12) =================
    # R01 - Detecção de edital/ano/tipo
    def t_r01():
        assert data_2026["edital"] == "unicamp", f"Edital incorreto: {data_2026['edital']}"
        assert data_2026["ano"] == 2026, f"Ano incorreto: {data_2026['ano']}"
        assert data_2026["tipo_prova"] == "Q-X", f"Tipo de prova incorreto: {data_2026['tipo_prova']}"
    suite.run("R01", "Detecção de edital/ano/tipo 2026", t_r01)

    # R02 - Total de páginas extraídas
    def t_r02():
        assert len(data_2026["paginas"]) == 27, f"Total de páginas incorreto: {len(data_2026['paginas'])}"
    suite.run("R02", "Total de páginas extraídas 2026", t_r02)

    # R03 - Total de questões extraídas
    def t_r03():
        assert len(data_2026["questoes"]) == 72, f"Total de questões incorreto: {len(data_2026['questoes'])}"
    suite.run("R03", "Total de questões extraídas 2026", t_r03)

    # R04 - Total de textos complementares
    def t_r04():
        assert len(data_2026["textos_comp"]) == 3, f"Total de textos complementares incorreto: {len(data_2026['textos_comp'])}"
    suite.run("R04", "Total de textos complementares 2026", t_r04)

    # R05 - Questão 1 tem imagens
    def t_r05():
        q1 = next(q for q in data_2026["questoes"] if q.metadados.numero == 1)
        assert len(q1.conteudo.url_img) >= 1, f"Questão 1 deveria ter pelo menos 1 imagem, mas tem {len(q1.conteudo.url_img)}"
    suite.run("R05", "Questão 1 tem imagens", t_r05)

    # R06 - Questão 2 tem exatamente 1 imagem de grupo
    def t_r06():
        q2 = next(q for q in data_2026["questoes"] if q.metadados.numero == 2)
        assert len(q2.conteudo.url_img) == 1, f"Questão 2 deveria ter exatamente 1 imagem de grupo, mas tem {len(q2.conteudo.url_img)}"
        assert "group" in q2.conteudo.url_img[0], f"A imagem da Q2 deveria ser um grupo, mas é: {q2.conteudo.url_img[0]}"
    suite.run("R06", "Questão 2 tem exatamente 1 imagem de grupo", t_r06)

    # R07 - Gabarito Q46: alternativa C correta
    def t_r07():
        q46 = next(q for q in data_2026["questoes"] if q.metadados.numero == 46)
        assert q46.alternativas.c.correta is True, "Alternativa C da Q46 deveria ser a correta"
    suite.run("R07", "Gabarito Q46: alternativa C correta", t_r07)

    # R08 - Gabarito Q46: demais alternativas erradas
    def t_r08():
        q46 = next(q for q in data_2026["questoes"] if q.metadados.numero == 46)
        assert q46.alternativas.a.correta is False, "Alternativa A da Q46 deveria ser incorreta"
        assert q46.alternativas.b.correta is False, "Alternativa B da Q46 deveria ser incorreta"
        assert q46.alternativas.d.correta is False, "Alternativa D da Q46 deveria ser incorreta"
    suite.run("R08", "Gabarito Q46: demais alternativas erradas", t_r08)

    # R09 - Questões salvas como JSON
    def t_r09():
        arquivos_json = [f for f in os.listdir(data_2026["pasta_saida"]) if f.endswith(".json") and not "_COMP" in f]
        assert len(arquivos_json) == 72, f"Total de arquivos JSON de questões incorreto: {len(arquivos_json)}"
    suite.run("R09", "Questões salvas como JSON", t_r09)

    # R10 - Textos complementares salvos
    def t_r10():
        arquivos_comp = [f for f in os.listdir(data_2026["pasta_saida"]) if "_COMP" in f]
        assert len(arquivos_comp) == 3, f"Total de arquivos JSON de textos complementares incorreto: {len(arquivos_comp)}"
    suite.run("R10", "Textos complementares salvos", t_r10)

    # R11 - Campos do schema presentes em Q1
    def t_r11():
        nome_q1 = f"{data_2026['edital']}_{data_2026['ano']}_{data_2026['tipo_prova'].replace('/', '-')}_1.json"
        with open(os.path.join(data_2026["pasta_saida"], nome_q1), "r", encoding="utf-8") as f:
            js = json.load(f)
            conteudo = js["conteudo"]
            assert "enunciado" in conteudo, "enunciado ausente no JSON"
            assert "url_img" in conteudo, "url_img ausente no JSON"
            assert "dificuldade" in conteudo, "dificuldade ausente no JSON"
            assert "resolucao" in conteudo, "resolucao ausente no JSON"
            assert "dica" in conteudo, "dica ausente no JSON"
            assert "objetiva" in conteudo, "objetiva ausente no JSON"
            assert conteudo["objetiva"] is True, "Questão 1 deveria ter objetiva=True"
            
            especificacao = js["especificacao"]
            assert "area" not in especificacao, "area não deveria estar no JSON segundo o contrato"
            assert "disciplina" in especificacao, "disciplina ausente na especificacao no JSON"
            assert "assunto" in especificacao, "assunto ausente na especificacao no JSON"
            assert "topicos" in especificacao, "topicos ausente na especificacao no JSON"
            
            assert isinstance(especificacao["disciplina"], list), "disciplina deveria ser lista"
            assert isinstance(especificacao["assunto"], list), "assunto deveria ser lista"
            assert isinstance(especificacao["topicos"], list), "topicos deveria ser lista"
            assert len(especificacao["disciplina"]) == 0, "disciplina deveria estar vazia"
            assert len(especificacao["assunto"]) == 0, "assunto deveria estar vazia"
            assert len(especificacao["topicos"]) == 0, "topicos deveria estar vazia"
    suite.run("R11", "Campos do schema presentes no JSON de Q1", t_r11)

    # R12 - dica é lista ou null
    def t_r12():
        q1 = next(q for q in data_2026["questoes"] if q.metadados.numero == 1)
        assert q1.conteudo.dica is None or isinstance(q1.conteudo.dica, list), f"dica deve ser lista ou None, tipo atual: {type(q1.conteudo.dica)}"
    suite.run("R12", "Dica é lista de strings ou null", t_r12)

    # ================= NEW COMPATIBILITY TESTS (N01 - N07) =================
    # N01 - Q66 tem exatamente 1 imagem de grupo (bloco A–H)
    def t_n01():
        q66 = next(q for q in data_2026["questoes"] if q.metadados.numero == 66)
        assert len(q66.conteudo.url_img) >= 1, f"Q66 deveria ter pelo menos uma imagem, mas tem {len(q66.conteudo.url_img)}"
        assert any("group" in img for img in q66.conteudo.url_img), "Q66 deveria conter uma imagem combinada agrupada (group)"
    suite.run("N01", "Q66 tem imagem de grupo (bloco A-H)", t_n01)

    # N02 - Q66: nenhuma imagem individual antiga
    def t_n02():
        q66 = next(q for q in data_2026["questoes"] if q.metadados.numero == 66)
        for img in q66.conteudo.url_img:
            assert "group" in img or "img0" in img, f"Q66 contém imagem individual incorreta em url_img: {img}"
    suite.run("N02", "Q66 sem imagens individuais antigas", t_n02)

    # N03 - Todas as imagens geradas são .webp
    def t_n03():
        imgs_dir = os.path.join(data_2026["pasta_saida"], "imgs")
        arquivos = os.listdir(imgs_dir)
        assert len(arquivos) > 0, "Nenhuma imagem foi gerada"
        for f in arquivos:
            assert f.endswith(".webp"), f"Imagem não foi convertida para WebP: {f}"
    suite.run("N03", "Todas as imagens geradas são .webp", t_n03)

    # N04 - JSON da Q1 contém campo dificuldade
    def t_n04():
        nome_q1 = f"{data_2026['edital']}_{data_2026['ano']}_{data_2026['tipo_prova'].replace('/', '-')}_1.json"
        with open(os.path.join(data_2026["pasta_saida"], nome_q1), "r", encoding="utf-8") as f:
            js = json.load(f)
            assert "dificuldade" in js["conteudo"], "Campo dificuldade ausente no JSON da Q1"
    suite.run("N04", "JSON de Q1 contém o campo dificuldade", t_n04)

    # N05 - Campo dificuldade é null inicialmente
    def t_n05():
        nome_q1 = f"{data_2026['edital']}_{data_2026['ano']}_{data_2026['tipo_prova'].replace('/', '-')}_1.json"
        with open(os.path.join(data_2026["pasta_saida"], nome_q1), "r", encoding="utf-8") as f:
            js = json.load(f)
            assert js["conteudo"]["dificuldade"] is None, f"Dificuldade da Q1 deveria ser None, valor: {js['conteudo']['dificuldade']}"
    suite.run("N05", "Campo dificuldade é null inicialmente", t_n05)

    # N06 - Gabarito de 2021 (múltiplos tipos): extrair_gabarito retorna lista
    def t_n06():
        assert os.path.exists(GABARITO_2021_PATH), f"Gabarito 2021 não encontrado em {GABARITO_2021_PATH}"
        res = extrair_gabarito(GABARITO_2021_PATH)
        assert isinstance(res, list), f"extrair_gabarito deveria retornar lista para gabarito múltiplo, retornou: {type(res)}"
        assert len(res) >= 2, f"Deveria ter extraído gabaritos de pelo menos 2 tipos de prova, extraiu: {len(res)}"
    suite.run("N06", "Gabarito de 2021 (múltiplos tipos) retorna lista", t_n06)

    # N07 - Gabarito de 2026 (tipo único): retorna tupla simples
    def t_n07():
        res = extrair_gabarito(GABARITO_PATH)
        assert isinstance(res, tuple), f"extrair_gabarito deveria retornar tupla para gabarito simples, retornou: {type(res)}"
        assert len(res) == 2, f"Tupla deveria ter tamanho 2, tem: {len(res)}"
        assert isinstance(res[0], dict), f"Primeiro elemento deve ser dict (respostas), é: {type(res[0])}"
        assert isinstance(res[1], str), f"Segundo elemento deve ser str (tipo), é: {type(res[1])}"
    suite.run("N07", "Gabarito de 2026 (tipo único) retorna tupla", t_n07)

    # ================= 2021 TESTS (E01 - E13) =================
    # E01 - Detecção edital/ano/tipo para 2021 E-G
    def t_e01():
        assert data_2021["edital"] == "unicamp", f"Edital incorreto: {data_2021['edital']}"
        assert data_2021["ano"] == 2021, f"Ano incorreto: {data_2021['ano']}"
        assert data_2021["tipo_prova"] == "E-G", f"Tipo de prova incorreto: {data_2021['tipo_prova']}"
    suite.run("E01", "Detecção edital/ano/tipo 2021 E-G", t_e01)

    # E02 - Q10 não contém drawing de texto como imagem
    def t_e02():
        q10 = next(q for q in data_2021["questoes"] if q.metadados.numero == 10)
        assert not any("drawing" in img for img in q10.conteudo.url_img), "Q10 não deve conter imagens de desenhos de texto"
    suite.run("E02", "Q10 não contém drawing de crônica como imagem", t_e02)

    # E03 - Q10 enunciado contém texto da crônica
    def t_e03():
        q10 = next(q for q in data_2021["questoes"] if q.metadados.numero == 10)
        assert "desigualdade" in q10.conteudo.enunciado.lower(), "Texto da crônica ausente no enunciado da Q10"
    suite.run("E03", "Q10 enunciado contém texto da crônica", t_e03)

    # E04 - Q20 imagens são individuais
    def t_e04():
        q20 = next(q for q in data_2021["questoes"] if q.metadados.numero == 20)
        assert len(q20.alternativas.a.url_img) == 1, "Alt A de Q20 deve ter 1 imagem"
        assert len(q20.alternativas.b.url_img) == 1, "Alt B de Q20 deve ter 1 imagem"
        assert len(q20.alternativas.c.url_img) == 1, "Alt C de Q20 deve ter 1 imagem"
        assert len(q20.alternativas.d.url_img) == 1, "Alt D de Q20 deve ter 1 imagem"
        assert all("img" in img[0] for img in [q20.alternativas.a.url_img, q20.alternativas.b.url_img, q20.alternativas.c.url_img, q20.alternativas.d.url_img]), "Imagens devem ser individuais"
    suite.run("E04", "Q20 imagens são individuais nas alternativas", t_e04)

    # E05 - Q23 imagens são individuais nas alternativas
    def t_e05():
        q23 = next(q for q in data_2021["questoes"] if q.metadados.numero == 23)
        assert len(q23.alternativas.a.url_img) == 1, "Alt A de Q23 deve ter 1 imagem"
        assert len(q23.alternativas.b.url_img) == 1, "Alt B de Q23 deve ter 1 imagem"
        assert len(q23.alternativas.c.url_img) == 1, "Alt C de Q23 deve ter 1 imagem"
        assert len(q23.alternativas.d.url_img) == 1, "Alt D de Q23 deve ter 1 imagem"
    suite.run("E05", "Q23 imagens são individuais nas alternativas", t_e05)

    # E06 - Q41 imagens de triângulos distribuídas
    def t_e06():
        q41 = next(q for q in data_2021["questoes"] if q.metadados.numero == 41)
        assert len(q41.alternativas.a.url_img) == 3, f"Alt A de Q41 deve ter 3 imagens de triângulos, tem {len(q41.alternativas.a.url_img)}"
        assert len(q41.alternativas.b.url_img) == 3, f"Alt B de Q41 deve ter 3 imagens de triângulos, tem {len(q41.alternativas.b.url_img)}"
        assert len(q41.alternativas.c.url_img) == 3, f"Alt C de Q41 deve ter 3 imagens de triângulos, tem {len(q41.alternativas.c.url_img)}"
        assert len(q41.alternativas.d.url_img) == 3, f"Alt D de Q41 deve ter 3 imagens de triângulos, tem {len(q41.alternativas.d.url_img)}"
    suite.run("E06", "Q41 imagens distribuídas de forma robusta", t_e06)

    # E07 - Q55 imagem tem margin top reduzida
    def t_e07():
        q55 = next(q for q in data_2021["questoes"] if q.metadados.numero == 55)
        assert len(q55.conteudo.enunciado) < 1500, "Enunciado da Q55 contém duplicações de texto espúrias"
    suite.run("E07", "Q55 sem duplicação de texto no enunciado", t_e07)

    # E08 - Q68 não agrupa página inteira
    def t_e08():
        imgs_dir = os.path.join(data_2021["pasta_saida"], "imgs")
        for f in os.listdir(imgs_dir):
            if "group" in f:
                with Image.open(os.path.join(imgs_dir, f)) as img:
                    largura_real = img.width / 2
                    assert largura_real <= 595.2 * 0.61, f"Imagem de grupo muito larga: {f} ({largura_real}px)"
    suite.run("E08", "Agrupamentos visuais respeitam limite de largura de coluna (60%)", t_e08)

    # E09 - Q70 e Q71 não misturam imagens
    def t_e09():
        q70 = next(q for q in data_2021["questoes"] if q.metadados.numero == 70)
        for img in q70.conteudo.url_img:
            assert "p19_" in img or "p20_" in img, f"Q70 tem imagem inválida: {img}"
    suite.run("E09", "Associação correta de imagens nas questões Q70/71", t_e09)

    # E10 - Filtro de drawings com texto
    def t_e10():
        page_4 = data_2021["doc"][4]
        rect_cronica = fitz.Rect(314, 87, 568, 429)
        assert drawing_eh_texto(page_4, rect_cronica) is True, "Desenho da crônica deveria ser classificado como texto"
    suite.run("E10", "drawing_eh_texto funciona", t_e10)

    # E11 - Detecção de coluna restritiva
    def t_e11():
        mid_x = 298
        r_leve = fitz.Rect(296, 100, 310, 200)
        assert coluna(r_leve, mid_x) == "D", "Deveria ser classificado como coluna D"
    suite.run("E11", "coluna com classificação restritiva", t_e11)

    # E12 - Padrão de alternativas detectado corretamente
    def t_e12():
        mid_x = 298
        elementos = [
            {"tipo": "raster", "rect": fitz.Rect(30, 100, 130, 180)},
            {"tipo": "raster", "rect": fitz.Rect(30, 200, 130, 280)},
            {"tipo": "raster", "rect": fitz.Rect(30, 300, 130, 380)}
        ]
        indices = detectar_padrao_alternativas(elementos, mid_x)
        assert len(indices) == 3, f"Deveria detectar os 3 elementos como padrão de alternativas, obteve {len(indices)}"
    suite.run("E12", "detectar_padrao_alternativas funciona", t_e12)

    # E13 - Split de alternativas limpo (sem 'b)' em A)
    def t_e13():
        q20 = next(q for q in data_2021["questoes"] if q.metadados.numero == 20)
        assert "b)" not in q20.alternativas.a.texto, "Alternativa A de Q20 contém o label b) incorretamente"
    suite.run("E13", "Split de alternativas limpo", t_e13)

    # ================= NEW BUGFIX AND IMPROVEMENT TESTS (F01 - F10) =================
    # F01 - Imagens com dimensão mínima (sem 2x2px)
    def t_f01():
        for img in data_2021["imagens"]:
            with Image.open(img["arquivo"]) as p_img:
                assert p_img.width >= 10 and p_img.height >= 10, f"Imagem minúscula extraída em 2021: {img['arquivo']} ({p_img.width}x{p_img.height})"
    suite.run("F01", "2021 E-G: nenhuma imagem extraída tem dimensão < 10px", t_f01)

    # F02 - Total de imagens razoável (B1 corrigido)
    def t_f02():
        # Sem o bug 2x2px, o total de imagens de 2021 E-G cai de 8.700+ para menos de 100
        assert len(data_2021["imagens"]) <= 150, f"Excesso de imagens em 2021: {len(data_2021['imagens'])}"
    suite.run("F02", "2021 E-G: total de imagens <= 150", t_f02)

    # F03 - Q71 com imagens (B2 corrigido)
    def t_f03():
        q71 = next(q for q in data_2021["questoes"] if q.metadados.numero == 71)
        assert len(q71.conteudo.url_img) >= 1, "Q71 não contém imagens (foram filtradas por overlap incorreto)"
    suite.run("F03", "2021 E-G: Q71 tem pelo menos 1 imagem no enunciado", t_f03)

    # F04 - Q70 com imagens (regressão de agrupamento)
    def t_f04():
        q70 = next(q for q in data_2021["questoes"] if q.metadados.numero == 70)
        assert len(q70.conteudo.url_img) >= 1, "Q70 deveria conter imagem"
    suite.run("F04", "2021 E-G: Q70 tem pelo menos 1 imagem no enunciado", t_f04)

    # F05 - 2023 Q-Z tipo detectado corretamente (B3 corrigido)
    def t_f05():
        assert data_2023_qz["tipo_prova"] == "Q-Z", f"Tipo de prova detectado incorretamente para 2023 Q-Z: {data_2023_qz['tipo_prova']}"
    suite.run("F05", "2023 Q-Z: tipo detectado corretamente como Q-Z", t_f05)

    # F06 - 2023 R-Y tipo detectado corretamente (B3 corrigido)
    def t_f06():
        assert data_2023_ry["tipo_prova"] == "R-Y", f"Tipo de prova detectado incorretamente para 2023 R-Y: {data_2023_ry['tipo_prova']}"
    suite.run("F06", "2023 R-Y: tipo detectado corretamente como R-Y", t_f06)

    # F07 - Gabarito 2025 com 72 respostas (B4 corrigido - asterisco)
    def t_f07():
        # A suíte do setup_for_pdf valida se extraímos todas
        assert len(data_2025["questoes"]) == 72, f"Total de questões esperado 72, obtido {len(data_2025['questoes'])}"
        
        # Check that all questions except annulled Q53 have Correta status mapped
        respostas_corretas = []
        for q in data_2025["questoes"]:
            has_correct = False
            for l in ["a", "b", "c", "d", "e"]:
                alt = getattr(q.alternativas, l)
                if alt and alt.correta:
                    has_correct = True
                    break
            if has_correct:
                respostas_corretas.append(q.metadados.numero)
                
        assert len(respostas_corretas) == 71, f"Esperado 71 respostas com alternativas corretas, obtido {len(respostas_corretas)}. Questão 53 é nula."
    suite.run("F07", "2025: gabarito extrai 72 respostas", t_f07)

    # F08 - Gabarito 2021 tipo limpo (B8 corrigido)
    def t_f08():
        res = extrair_gabarito(GABARITO_2021_PATH)
        for _, tipo in res:
            assert "\n" not in tipo, f"Gabarito tipo contém newline residual: {repr(tipo)}"
    suite.run("F08", "2021: tipo gabarito não contém \\n", t_f08)

    # F09 - Integridade dos arquivos de imagem em disco
    def t_f09():
        for dataset in [data_2026, data_2021, data_2022, data_2023_qz, data_2024_qy, data_2025]:
            for img in dataset["imagens"]:
                caminho = img["arquivo"]
                if os.path.exists(caminho):
                    sz = os.path.getsize(caminho)
                    assert sz > 50, f"Arquivo de imagem corrompido ou vazio (<= 50 bytes): {caminho} ({sz} bytes)"
    suite.run("F09", "Todas imagens em disco têm > 100 bytes", t_f09)

    # F10 - 2024 Q-Y Mapeamento de alternativas lado a lado na Q67 (B9 corrigido)
    def t_f10():
        q67 = next(q for q in data_2024_qy["questoes"] if q.metadados.numero == 67)
        assert len(q67.alternativas.a.url_img) == 1, f"Alt A deveria ter exatamente 1 imagem, tem {len(q67.alternativas.a.url_img)}"
        assert len(q67.alternativas.b.url_img) == 1, f"Alt B deveria ter exatamente 1 imagem, tem {len(q67.alternativas.b.url_img)}"
        assert len(q67.alternativas.c.url_img) == 1, f"Alt C deveria ter exatamente 1 imagem, tem {len(q67.alternativas.c.url_img)}"
        assert len(q67.alternativas.d.url_img) == 1, f"Alt D deveria ter exatamente 1 imagem, tem {len(q67.alternativas.d.url_img)}"
    suite.run("F10", "2024 Q-Y: imagens das alternativas de Q67 mapeadas de forma 1-para-1 a, b, c, d", t_f10)

    # ================= UNIT TESTS (U01 - U08) =================
    # U01 - drawing_eh_texto: texto denso
    def t_u01():
        page_4 = data_2021["doc"][4]
        rect = fitz.Rect(314, 87, 568, 429)
        assert drawing_eh_texto(page_4, rect) is True
    suite.run("U01", "Unit test drawing_eh_texto (texto denso)", t_u01)

    # U02 - drawing_eh_texto: vazio/gráfico
    def t_u02():
        page_8 = data_2021["doc"][8]
        rect = fitz.Rect(41.2, 411.2, 136.0, 497.2)
        assert drawing_eh_texto(page_8, rect) is False
    suite.run("U02", "Unit test drawing_eh_texto (vazio/gráfico)", t_u02)

    # U03 - coluna: esquerda puro
    def t_u03():
        r = fitz.Rect(20, 100, 250, 200)
        assert coluna(r, 298) == "E"
    suite.run("U03", "Unit test coluna (esquerda puro)", t_u03)

    # U04 - coluna: direita puro
    def t_u04():
        r = fitz.Rect(320, 100, 550, 200)
        assert coluna(r, 298) == "D"
    suite.run("U04", "Unit test coluna (direita puro)", t_u04)

    # U05 - coluna: centro cruzando significativamente
    def t_u05():
        r = fitz.Rect(100, 100, 500, 200)
        assert coluna(r, 298) == "C"
    suite.run("U05", "Unit test coluna (cruzando significativamente)", t_u05)

    # U06 - coluna: centro cruzando marginalmente (não C)
    def t_u06():
        r_marginal = fitz.Rect(296, 100, 350, 200)
        assert coluna(r_marginal, 298) == "D"
    suite.run("U06", "Unit test coluna (cruzando marginalmente)", t_u06)

    # U07 - detectar_padrao_alternativas: 3 imagens similares
    def t_u07():
        elementos = [
            {"tipo": "raster", "rect": fitz.Rect(30, 100, 130, 180)},
            {"tipo": "raster", "rect": fitz.Rect(30, 200, 130, 280)},
            {"tipo": "raster", "rect": fitz.Rect(30, 300, 130, 380)}
        ]
        indices = detectar_padrao_alternativas(elementos, 298)
        assert len(indices) == 3
    suite.run("U07", "Unit test detectar_padrao_alternativas (3 imagens)", t_u07)

    # U08 - detectar_padrao_alternativas: 2 imagens
    def t_u08():
        elementos = [
            {"tipo": "raster", "rect": fitz.Rect(30, 100, 130, 180)},
            {"tipo": "raster", "rect": fitz.Rect(30, 200, 130, 280)}
        ]
        indices = detectar_padrao_alternativas(elementos, 298)
        assert len(indices) == 0
    suite.run("U08", "Unit test detectar_padrao_alternativas (2 imagens)", t_u08)

    # ================= NOVOS TESTES DE CORRETUDE DE LAYOUT (T01 - T05) =================
    # T01 - 2022 Q22 alternativas horizontais
    def t_horiz_2022():
        q22 = next(q for q in data_2022["questoes"] if q.metadados.numero == 22)
        assert q22.alternativas.c is not None and q22.alternativas.c.texto, "Alternativa C da Q22 de 2022 vazia"
        assert q22.alternativas.d is not None and q22.alternativas.d.texto, "Alternativa D da Q22 de 2022 vazia"
    suite.run("T_HORIZ_2022", "2022 Q22: alternativas horizontais separadas corretamente", t_horiz_2022)

    # T02 - 2024 Q65 alternativas horizontais
    def t_horiz_2024():
        q65 = next(q for q in data_2024_qy["questoes"] if q.metadados.numero == 65)
        assert all(getattr(q65.alternativas, letra) and getattr(q65.alternativas, letra).texto for letra in "abcd"), "Uma ou mais alternativas da Q65 de 2024 estão vazias"
    suite.run("T_HORIZ_2024", "2024 Q65: alternativas horizontais separadas corretamente", t_horiz_2024)

    # T03 - 2021 Q33-Q40 Física (notação científica / expoentes)
    def t_fisica_2021():
        for num in range(33, 41):
            q = next(q for q in data_2021["questoes"] if q.metadados.numero == num)
            assert all(getattr(q.alternativas, letra) and getattr(q.alternativas, letra).texto for letra in "abcd"), f"Uma ou mais alternativas da Q{num} de 2021 estão vazias (potência/expoente quebrados)"
    suite.run("T_FISICA_2021", "2021 Q33-Q40: alternativas de física preenchidas sem fragmentação", t_fisica_2021)

    # T04 - 2026 Q33-Q34 layout Zuzu Angel / Jus soli
    def t_img_map_2026():
        q33 = next(q for q in data_2026["questoes"] if q.metadados.numero == 33)
        assert q33.alternativas.c is not None and q33.alternativas.c.texto, "Q33 de 2026 alternativa C vazia"
        q34 = next(q for q in data_2026["questoes"] if q.metadados.numero == 34)
        assert len(q34.conteudo.enunciado.strip()) > 50, f"Q34 de 2026 enunciado truncado: {q34.conteudo.enunciado}"
    suite.run("T_IMG_MAP_2026", "2026 Q33-Q34: layout complexo Zuzu Angel / nacionalidade separado corretamente", t_img_map_2026)

    # T05 - 2021 Q18 Imagem OMS
    def t_img_map_2021():
        q18 = next(q for q in data_2021["questoes"] if q.metadados.numero == 18)
        assert len(q18.conteudo.url_img) == 1, f"Q18 de 2021 deveria ter 1 imagem (cartaz OMS), mas tem {len(q18.conteudo.url_img)}"
    suite.run("T_IMG_MAP_2021", "2021 Q18: imagem do cartaz OMS associada corretamente ao enunciado", t_img_map_2021)

    # ================= 2026 SECOND PHASE TESTS =================
    # D01 - Detecção e quantidade de questões discursivas
    def t_d01():
        assert len(data_2026_2fase["questoes"]) == 10, f"Deveria extrair exatamente 10 questões discursivas, extraiu {len(data_2026_2fase['questoes'])}"
    suite.run("D01", "2026 2ª Fase: quantidade de questões extraídas", t_d01)

    # D02 - Verificação de metadados e sub_itens
    def t_d02():
        q1 = next(q for q in data_2026_2fase["questoes"] if q.metadados.numero == 1)
        assert q1.alternativas is None, "Questão dissertativa não deve conter alternativas"
        assert not hasattr(q1, "sub_itens") or q1.sub_itens is None, "Questão dissertativa não deve conter o campo sub_itens"
        assert "a)" in q1.conteudo.enunciado, "Sub-item a) deve estar no enunciado"
        assert "b)" in q1.conteudo.enunciado, "Sub-item b) deve estar no enunciado"
        assert "mecanismo linguístico" in q1.conteudo.enunciado.lower(), "Texto do sub-item a) incorreto ou incompleto"
    suite.run("D02", "2026 2ª Fase: estrutura e conteúdo dos sub-itens da Q1", t_d02)

    suite.report()


if __name__ == "__main__":
    main()
