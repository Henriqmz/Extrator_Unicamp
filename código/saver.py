import os
import json

def salvar_questoes(questoes, pasta="questoes_json"):
    os.makedirs(pasta, exist_ok=True)

    for q in questoes:
        nome = f"{pasta}/questao_{q.metadados.numero}.json"

        with open(nome, "w", encoding="utf-8") as f:
            json.dump(q.model_dump(), f, ensure_ascii=False, indent=2)


def salvar_textos(textos, pasta="textos_json"):
    os.makedirs(pasta, exist_ok=True)

    for t in textos:
        cod = "_".join(t.metadadosComp.codigos_questoes)
        nome = f"{pasta}/texto_{cod}.json"

        with open(nome, "w", encoding="utf-8") as f:
            json.dump(t.model_dump(), f, ensure_ascii=False, indent=2)