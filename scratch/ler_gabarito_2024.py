import fitz
doc = fitz.open("Provas/provas-e-gabaritos-unicamp-2024/provas-e-gabaritos-unicamp-2024/gabarito-p-y-unicamp-2024.pdf")
for page in doc:
    print(page.get_text())
