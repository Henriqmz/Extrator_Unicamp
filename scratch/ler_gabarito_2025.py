import fitz
doc = fitz.open("Provas/2-provas-e-gabaritos-unicamp-2025/provas-e-gabaritos-unicamp-2025/provas-e-gabaritos-unicamp-vestibular-2025/1-fase-provas-gabaritos-unicamp-vestibular-2025/gabarito-q-z-1-fase-unicamp-2025.pdf")
for page in doc:
    print(page.get_text())
