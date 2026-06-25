import fitz
from extractor import extrair_pdf, encontrar_labels_alternativas, map_image, extrair_imagens

# 1. Analisar 2021 Página 6 (Q18 - Cartaz OMS) e Página 7 (Q20 - Alternativas com Imagens)
print("=== ANALISANDO 2021 E-G ===")
doc_2021 = fitz.open("Provas/1-provas-e-gabaritos-unicamp-2021/1ª fase/Provas E e G.pdf")
mid_x_2021 = doc_2021[0].rect.width / 2

for pag_num in [6, 7]:
    print(f"\n--- PAGINA {pag_num} ---")
    page = doc_2021[pag_num]
    labels = encontrar_labels_alternativas(page, mid_x_2021)
    print("Labels encontrados:", labels)
    
    # Extrair imagens da página usando a lógica padrão
    # (Para simular, vamos extrair os retângulos de imagem usando page.get_images)
    for i, img in enumerate(page.get_images(full=True)):
        xref = img[0]
        rects = page.get_image_rects(xref)
        for r in rects:
            centro_x = (r.x0 + r.x1) / 2
            letra = map_image(r.y0, centro_x, mid_x_2021, labels, img_w=r.width, page=page)
            print(f"Imagem xref={xref}, rect={r}, centro_x={centro_x:.2f}, y0={r.y0:.2f}, w={r.width:.2f} -> mapeado para: {letra}")

# 2. Analisar 2026 Página 13 (Zuzu Angel Q33)
print("\n=== ANALISANDO 2026 Q-X ===")
doc_2026 = fitz.open("Provas/provas-e-gabaritos-unicamp-2026/1-fase-unicamp-2026/prova-q-x-1-fase-unicamp-2026.pdf")
mid_x_2026 = doc_2026[0].rect.width / 2
page_2026 = doc_2026[13] # Pag 13
labels_2026 = encontrar_labels_alternativas(page_2026, mid_x_2026)
print("Labels encontrados na pag 13 (2026):", labels_2026)
for i, img in enumerate(page_2026.get_images(full=True)):
    xref = img[0]
    rects = page_2026.get_image_rects(xref)
    for r in rects:
        centro_x = (r.x0 + r.x1) / 2
        letra = map_image(r.y0, centro_x, mid_x_2026, labels_2026, img_w=r.width, page=page_2026)
        print(f"Imagem xref={xref}, rect={r}, centro_x={centro_x:.2f}, y0={r.y0:.2f}, w={r.width:.2f} -> mapeado para: {letra}")
