import fitz
from extractor import extrair_texto, extrair_pdf

paginas, doc = extrair_pdf("Provas/provas-e-gabaritos-unicamp-2026/1-fase-unicamp-2026/prova-q-x-1-fase-unicamp-2026.pdf")
p13 = [p for p in paginas if p["numero"] == 13]
texto_p13 = extrair_texto(p13)
print("TEXTO EXTRAIDO DA PAGINA 13 DE 2026:")
print(texto_p13)
