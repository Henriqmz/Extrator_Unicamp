import fitz
import os

def extrair_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    paginas = []

    for page_num, page in enumerate(doc):
        blocks = page.get_text("blocks")
        paginas.append({
            "numero": page_num,
            "blocks": blocks,
            "page": page
        })

    return paginas, doc


def extrair_texto(paginas):
    texto = ""
    for p in paginas:
        for b in p["blocks"]:
            texto += b[4] + "\n"
    return texto


def extrair_imagens(doc, output_dir="imgs"):
    os.makedirs(output_dir, exist_ok=True)

    imagens = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        imgs = page.get_images(full=True)

        for i, img in enumerate(imgs):
            xref = img[0]
            base = doc.extract_image(xref)

            nome = f"{output_dir}/p{page_index}_img{i}.{base['ext']}"

            with open(nome, "wb") as f:
                f.write(base["image"])

            rects = page.get_image_rects(xref)

            for r in rects:
                imagens.append({
                    "pagina": page_index,
                    "y": r.y0,
                    "arquivo": nome
                })

    return imagens