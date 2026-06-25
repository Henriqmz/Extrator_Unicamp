import fitz

def analisar_paginas_2021():
    doc = fitz.open("Provas/1-provas-e-gabaritos-unicamp-2021/1ª fase/Provas E e G.pdf")
    for page_idx, page in enumerate(doc):
        page_width = page.rect.width
        mid_x = page_width / 2
        d = page.get_text("dict")
        
        total_linhas = 0
        linhas_cruzam = 0
        
        for b in d["blocks"]:
            if b["type"] == 0:
                for line in b["lines"]:
                    total_linhas += 1
                    x0, y0, x1, y1 = line["bbox"]
                    if x0 < mid_x - 40 and x1 > mid_x + 40:
                        linhas_cruzam += 1
                        
        pct = (linhas_cruzam / total_linhas * 100) if total_linhas > 0 else 0
        layout = "UNICA" if pct > 12 else "DUAS_COLUNAS"
        print(f"Pag {page_idx:02d}: total={total_linhas}, cruzam={linhas_cruzam} ({pct:.1f}%) -> LAYOUT DETECTADO: {layout}")

analisar_paginas_2021()
