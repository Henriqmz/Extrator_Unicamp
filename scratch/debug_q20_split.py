import os
import sys
import re
import json

BASE_DIR = r"C:/Users/tocoa/OneDrive/Área de Trabalho/Ike/Projeto"
sys.path.insert(0, BASE_DIR)
JSON_PATH = os.path.join(BASE_DIR, "unicamp_2021_test_E-G", "unicamp_2021_E-G_20.json")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    q20_data = json.load(f)

print("=== Q20 JSON ATUAL ===")
print(json.dumps(q20_data["alternativas"], indent=2, ensure_ascii=False))

# Vamos ver o texto bruto extraído para a Questão 20
# Para isso, precisamos rodar a extração até extrair_questoes
from extractor import *
from processor import *

PDF_PATH = os.path.join(BASE_DIR, "Provas", "1-provas-e-gabaritos-unicamp-2021", "1ª fase", "Provas E e G.pdf")
paginas, doc = extrair_pdf(PDF_PATH)
prefixo_img = "debug_split"
imagens = extrair_imagens(doc, output_dir=os.path.join(BASE_DIR, "scratch", "temp_imgs_split"), prefixo=prefixo_img)
texto = extrair_texto(paginas, imagens)

# Buscar o bloco de texto correspondente à Questão 20
padrao = r"(QUESTÃO\s+(20))(.*?)(?=QUESTÃO\s+21|\Z)"
match = re.search(padrao, texto, re.DOTALL)
if match:
    bloco = match.group(3).strip()
    print("\n=== BLOCO BRUTO QUESTÃO 20 ===")
    print(repr(bloco))
    
    bloco_proc = re.sub(r'(?<!\n)\s+\b([b-e])\)\s+', r'\n\1) ', bloco)
    print("\n=== BLOCO APÓS PRÉ-PROCESSAMENTO ===")
    print(repr(bloco_proc))
    
    partes = re.split(r"\n\s*([a-e])\)\s*", bloco_proc)
    print("\n=== PARTES APÓS SPLIT ===")
    for idx, p in enumerate(partes):
        print(f"Parte {idx}: {repr(p)}")
