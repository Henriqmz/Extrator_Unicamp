import fitz

def testar_agrupamento_distancia():
    doc = fitz.open("Provas/provas-e-gabaritos-unicamp-2026/1-fase-unicamp-2026/prova-q-x-1-fase-unicamp-2026.pdf")
    page = doc[13] # Pag 13
    page_width = page.rect.width
    mid_x = page_width / 2
    
    d = page.get_text("dict")
    raw_lines = {"esquerda": [], "direita": []}
    
    # 1. Detectar layout
    total_linhas = 0
    linhas_cruzam = 0
    for b in d["blocks"]:
        if b["type"] == 0:
            for line in b["lines"]:
                line_text = "".join(span["text"] for span in line["spans"])
                if not line_text.strip():
                    continue
                total_linhas += 1
                x0, y0, x1, y1 = line["bbox"]
                if x0 < mid_x - 40 and x1 > mid_x + 40:
                    linhas_cruzam += 1
    pct = (linhas_cruzam / total_linhas * 100) if total_linhas > 0 else 0
    layout_coluna_unica = pct > 12.0
    print(f"LAYOUT DETECTADO: {'UNICA' if layout_coluna_unica else 'DUAS_COLUNAS'} ({pct:.1f}% cruzam)")
    
    for b in d["blocks"]:
        if b["type"] == 0:
            for line in b["lines"]:
                line_text = "".join(span["text"] for span in line["spans"])
                if not line_text.strip():
                    continue
                x0, y0, x1, y1 = line["bbox"]
                if layout_coluna_unica:
                    col = "esquerda"
                else:
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
        if not lines:
            continue
        lines.sort(key=lambda x: x["y"])
        
        grouped = []
        for l in lines:
            if not grouped:
                grouped.append([l])
            else:
                ultimo_grupo = grouped[-1]
                media_y = sum(item["y"] for item in ultimo_grupo) / len(ultimo_grupo)
                if abs(l["y"] - media_y) < 6.0:
                    ultimo_grupo.append(l)
                else:
                    grouped.append([l])
                    
        processadas = []
        for g in grouped:
            g.sort(key=lambda x: x["x"])
            texto_completo = ""
            ultimo_x1 = None
            for item in g:
                txt = item["texto"]
                x0, _, x1, _ = item["bbox"]
                
                if ultimo_x1 is not None and x0 - ultimo_x1 > 15.0:
                    texto_completo += "\n" + txt
                else:
                    if txt.startswith("\t") or txt.startswith(" ") or texto_completo.endswith("\t") or texto_completo.endswith(" "):
                        texto_completo += txt
                    else:
                        texto_completo += " " + txt if texto_completo else txt
                ultimo_x1 = x1
                
            processadas.append({
                "texto": texto_completo.strip(),
                "y": g[0]["y"]
            })
            
        print(f"\n--- COLUNA {col.upper()} ---")
        for p in processadas:
            print(f"y={p['y']:.2f}:\n{p['texto']}")

testar_agrupamento_distancia()
