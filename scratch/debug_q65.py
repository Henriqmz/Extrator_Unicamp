import fitz
from extractor import extrair_texto, extrair_pdf

paginas, doc = extrair_pdf("Provas/provas-e-gabaritos-unicamp-2024/provas-e-gabaritos-unicamp-2024/provas-q-y-unicamp-1-fase-2024.pdf")
# Q65 está na página 19 (índice 19)
p19 = [p for p in paginas if p["numero"] == 19]
texto_p19 = extrair_texto(p19)
print("TEXTO EXTRAIDO DA PAGINA 19:")
print(texto_p19)
