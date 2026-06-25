import fitz
doc = fitz.open("Provas/2-provas-e-gabaritos-unicamp-2022/Primeira fase/gabarito-1-fase.pdf")
for page in doc:
    print(page.get_text())
