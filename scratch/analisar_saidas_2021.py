import os
import sys
import json
import fitz

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

PDF_2021_PATH = os.path.join(BASE_DIR, "Provas", "1-provas-e-gabaritos-unicamp-2021", "1ª fase", "Provas E e G.pdf")
JSON_DIR = os.path.join(BASE_DIR, "unicamp_2021_test_E-G")

doc = fitz.open(PDF_2021_PATH)

def check_question(num):
    json_path = os.path.join(JSON_DIR, f"unicamp_2021_E-G_{num}.json")
    if not os.path.exists(json_path):
        return f"JSON para Q{num} não encontrado."
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    enunciado = data["conteudo"]["enunciado"]
    url_img = data["conteudo"]["url_img"]
    
    res = []
    res.append(f"=== QUESTÃO {num} ===")
    res.append(f"Imagens no enunciado: {url_img}")
    res.append(f"Primeiras linhas do enunciado: {repr(enunciado[:120])}")
    
    for l in ["a", "b", "c", "d", "e"]:
        alt = data["alternativas"].get(l)
        if alt:
            res.append(f"  Alt {l} (correta: {alt.get('correta')}): {repr(alt.get('texto')[:100])}")
            if alt.get("url_img"):
                res.append(f"    Imagens na Alt {l}: {alt.get('url_img')}")
        else:
            res.append(f"  Alt {l}: Não especificada")
            
    return "\n".join(res)

# Verificar as questões mais críticas de 2021
questoes_para_analisar = [10, 18, 20, 23, 33, 40, 41, 55, 68, 70, 71]

print("Análise automatizada de conformidade física vs JSON para Unicamp 2021 (Provas E e G):")
print(f"Diretório JSON: {JSON_DIR}")
print(f"PDF original: {PDF_2021_PATH}\n")

for q in questoes_para_analisar:
    print(check_question(q))
    print("-" * 50)
