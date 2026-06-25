import fitz
doc = fitz.open("Provas/provas-e-gabaritos-unicamp-2026/1-fase-unicamp-2026/gabarito-q-x-1-fase-unicamp-2026.pdf")
for page in doc:
    print(page.get_text())
