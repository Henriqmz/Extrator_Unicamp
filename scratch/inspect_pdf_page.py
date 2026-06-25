import fitz

doc = fitz.open("Provas/provas-e-gabaritos-unicamp-2026/1-fase-unicamp-2026/prova-q-x-1-fase-unicamp-2026.pdf")
print("PAGE 12 TEXT:")
print(doc[12].get_text())
print("\nPAGE 13 TEXT:")
print(doc[13].get_text())
