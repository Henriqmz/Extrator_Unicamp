import fitz

def testar_agrupamento():
    doc = fitz.open("Provas/provas-e-gabaritos-unicamp-2024/provas-e-gabaritos-unicamp-2024/provas-q-y-unicamp-1-fase-2024.pdf")
    page = doc[19]
    page_width = page.rect.width
    mid_x = page_width / 2
    
    d = page.get_text("dict")
    raw_lines = {"esquerda": [], "direita": []}
    
    for b in d["blocks"]:
        if b["type"] == 0:  # Texto
            for line in b["lines"]:
                line_text = "".join(span["text"] for span in line["spans"])
                if not line_text.strip():
                    continue
                x0, y0, x1, y1 = line["bbox"]
                centro_x = (x0 + x1) / 2
                col = "esquerda" if centro_x < mid_x else "direita"
                raw_lines[col].append({
                    "texto": line_text,
                    "y": y0,
                    "x": x0,
                    "bbox": line["bbox"]
                })
                
    for col in ["esquerda", "direita"]:
        lines = raw_lines[col]
        lines.sort(key=lambda x: x["y"])
        
        # Agrupar linhas com Y próximo (< 6px)
        grouped = []
        for l in lines:
            if not grouped:
                grouped.append([l])
            else:
                # Verificar se o Y difere por menos de 6px do último grupo
                ultimo_grupo = grouped[-1]
                media_y = sum(item["y"] for item in ultimo_grupo) / len(ultimo_grupo)
                if abs(l["y"] - media_y) < 6.0:
                    ultimo_grupo.append(l)
                else:
                    grouped.append([l])
                    
        # Concatenar cada grupo ordenando por X
        processadas = []
        for g in grouped:
            g.sort(key=lambda x: x["x"])
            # Concatenar textos. Se houver espaços ou tabulações, podemos juntar com espaço
            texto_completo = ""
            for item in g:
                txt = item["texto"]
                if txt.startswith("\t") or txt.startswith(" ") or texto_completo.endswith("\t") or texto_completo.endswith(" "):
                    texto_completo += txt
                else:
                    texto_completo += " " + txt if texto_completo else txt
            
            # Limpar espaços duplos
            texto_completo = re_sub_spaces(texto_completo)
            
            processadas.append({
                "texto": texto_completo.strip(),
                "y": g[0]["y"]
            })
            
        print(f"\n--- COLUNA {col.upper()} PROCESSADA ---")
        for p in processadas:
            print(f"y={p['y']:.2f}: {repr(p['texto'])}")

def re_sub_spaces(txt):
    import re
    return re.sub(r' {2,}', ' ', txt)

testar_agrupamento()
