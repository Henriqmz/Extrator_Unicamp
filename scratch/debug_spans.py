import fitz
doc = fitz.open("Provas/provas-e-gabaritos-unicamp-2024/provas-e-gabaritos-unicamp-2024/provas-q-y-unicamp-1-fase-2024.pdf")
page = doc[19]
print("SPANS NA PAGINA 19:")
for b in page.get_text("dict")["blocks"]:
    if b["type"] == 0:
        for line in b["lines"]:
            for span in line["spans"]:
                print(f"y0={line['bbox'][1]:.2f}, x0={line['bbox'][0]:.2f}, text={repr(span['text'])}")
