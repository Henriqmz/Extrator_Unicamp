import re
from models import *

# -----------------------
# TEXTOS COMPLEMENTARES
# -----------------------

def extrair_textos_comp(texto):
    padrao = r"(Texto para as questões ([\d,\se]+)\.\n)(.*?)(?=QUESTÃO|\Z)"
    resultados = []

    for match in re.finditer(padrao, texto, re.DOTALL):
        numeros = re.findall(r"\d+", match.group(2))
        conteudo = match.group(3).strip()

        resultados.append(
            TextoComplementar(
                metadadosComp=MetadadosComp(codigos_questoes=numeros),
                conteudoComp=ConteudoComp(enunciado=conteudo)
            )
        )

    return resultados


# -----------------------
# QUESTÕES
# -----------------------

def extrair_questoes(texto):
    padrao = r"(QUESTÃO\s+(\d+))(.*?)(?=QUESTÃO\s+\d+|\Z)"
    questoes = []

    for match in re.finditer(padrao, texto, re.DOTALL):
        numero = int(match.group(2))
        bloco = match.group(3).strip()

        partes = re.split(r"\n[a-d]\)", bloco)
        enunciado = partes[0].strip()

        alternativas_txt = re.findall(r"\n([a-d])\)\s*(.*)", bloco)

        alt_dict = {}
        for letra, txt in alternativas_txt:
            alt_dict[letra] = AlternativaItem(texto=txt.strip())

        questoes.append(
            Questao(
                metadados=Metadados(
                    codigo=f"unicamp_2026_q{numero}",
                    edital="unicamp",
                    numero=numero,
                    tipo_ou_cor="Q/X",
                    ano=2026
                ),
                conteudo=Conteudo(enunciado=enunciado),
                especificacao=Especificacao(materia="desconhecida", tags=[]),
                alternativas=Alternativas(
                    a=alt_dict.get("a", AlternativaItem()),
                    b=alt_dict.get("b", AlternativaItem()),
                    c=alt_dict.get("c", AlternativaItem()),
                    d=alt_dict.get("d", AlternativaItem())
                )
            )
        )

    return questoes


# -----------------------
# MAPEAMENTOS
# -----------------------

def mapear_textos_comp(textos_comp):
    mapa = {}
    for t in textos_comp:
        for cod in t.metadadosComp.codigos_questoes:
            mapa[int(cod)] = t
    return mapa


def localizar_questoes(paginas):
    posicoes = []

    for p in paginas:
        for b in p["blocks"]:
            match = re.search(r"QUESTÃO\s+(\d+)", b[4])
            if match:
                posicoes.append({
                    "numero": int(match.group(1)),
                    "pagina": p["numero"],
                    "y": b[1]
                })

    posicoes.sort(key=lambda x: (x["pagina"], x["y"]))
    return posicoes


def associar_imagens(questoes_pos, imagens):
    mapa = {q["numero"]: [] for q in questoes_pos}

    for img in imagens:
        melhor = None
        menor = float("inf")

        for q in questoes_pos:
            if q["pagina"] == img["pagina"]:
                dist = abs(q["y"] - img["y"])
                if dist < menor:
                    menor = dist
                    melhor = q["numero"]

        if melhor:
            mapa[melhor].append(img["arquivo"])

    return mapa


def enriquecer(questoes, mapa_textos, mapa_imgs):
    for q in questoes:
        num = q.metadados.numero

        if num in mapa_textos:
            q.conteudo.enunciado = (
                mapa_textos[num].conteudoComp.enunciado +
                "\n\n" +
                q.conteudo.enunciado
            )

        if num in mapa_imgs and mapa_imgs[num]:
            q.conteudo.url_img = mapa_imgs[num][0]

    return questoes