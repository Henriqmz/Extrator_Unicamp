import os
import glob
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

projeto_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
exec_dir = os.path.join(projeto_root, "exec_results")

resumo_file = os.path.join(exec_dir, "resumo_execucao.json")
if not os.path.exists(resumo_file):
    print(f"⚠️ Resumo de execução não encontrado em: {resumo_file}")
    sys.exit(1)

with open(resumo_file, "r", encoding="utf-8") as f:
    resumo_dados = json.load(f)

relatorio_analise = []

for item in resumo_dados:
    nome = item["nome"]
    pasta = item["pasta"]
    tipo = item["tipo"]
    ano = item["ano"]

    json_files = glob.glob(os.path.join(pasta, "*.json"))

    questoes_com_problema_enunciado = []
    questoes_com_simbolos_estranhos = []
    questoes_com_cabecalho_no_texto = []
    imagens_quebradas = []
    total_imgs_vinculadas = 0
    total_q_processadas = 0

    for jf in json_files:
        if "resumo" in os.path.basename(jf).lower() or "textos_comp" in os.path.basename(jf).lower():
            continue
        try:
            with open(jf, "r", encoding="utf-8") as qf:
                qdata = json.load(qf)
        except Exception:
            continue

        if not isinstance(qdata, dict) or "metadados" not in qdata:
            continue

        total_q_processadas += 1
        num_q = qdata["metadados"].get("numero", 0)
        conteudo = qdata.get("conteudo", {})
        enunciado = conteudo.get("enunciado", "")
        imgs_enunciado = conteudo.get("url_img") or []

        if not enunciado or len(enunciado.strip()) < 10:
            questoes_com_problema_enunciado.append(num_q)

        if re.search(r"\bQUESTÃO\s+\d+\b", enunciado) and not re.match(r"^\s*QUESTÃO\s+\d+", enunciado):
            questoes_com_cabecalho_no_texto.append(num_q)

        if re.search(r"[\u0d00-\u0d7f\u1200-\u137f\U0001d400-\U0001d7ff]", enunciado):
            questoes_com_simbolos_estranhos.append(num_q)

        for img_rel in imgs_enunciado:
            total_imgs_vinculadas += 1
            img_abs = os.path.normpath(os.path.join(pasta, img_rel))
            if not os.path.exists(img_abs) or os.path.getsize(img_abs) < 50:
                imagens_quebradas.append(img_rel)

        if conteudo.get("objetiva") and qdata.get("alternativas"):
            alts = qdata["alternativas"]
            if isinstance(alts, dict):
                for letra in ["a", "b", "c", "d", "e"]:
                    alt_obj = alts.get(letra)
                    if alt_obj and isinstance(alt_obj, dict):
                        imgs_alt = alt_obj.get("url_img") or []
                        for img_rel in imgs_alt:
                            total_imgs_vinculadas += 1
                            img_abs = os.path.normpath(os.path.join(pasta, img_rel))
                            if not os.path.exists(img_abs) or os.path.getsize(img_abs) < 50:
                                imagens_quebradas.append(img_rel)

    relatorio_analise.append({
        "nome": nome,
        "ano": ano,
        "tipo": tipo,
        "total_questoes_json": total_q_processadas,
        "total_imgs_vinculadas": total_imgs_vinculadas,
        "questoes_enunciado_suspeito": questoes_com_problema_enunciado,
        "questoes_cabecalho_residual": questoes_com_cabecalho_no_texto,
        "questoes_simbolos_unicode": questoes_com_simbolos_estranhos,
        "imagens_quebradas": imagens_quebradas
    })

analise_output = os.path.join(exec_dir, "relatorio_analise_qualidade.json")
with open(analise_output, "w", encoding="utf-8") as f:
    json.dump(relatorio_analise, f, indent=2, ensure_ascii=False)

print(f"📊 Relatório de qualidade gerado em: {analise_output}\n")
for r in relatorio_analise:
    print(f"[{r['nome']}] Ano: {r['ano']} | Tipo: {r['tipo']}")
    print(f"  • Questões JSON: {r['total_questoes_json']}")
    print(f"  • Imagens vinculadas no JSON: {r['total_imgs_vinculadas']}")
    print(f"  • Imagens quebradas/ausentes: {len(r['imagens_quebradas'])}")
    print(f"  • Enunciados suspeitos (<10 chars): {len(r['questoes_enunciado_suspeito'])}")
    print(f"  • Símbolos Unicode estranhos: {len(r['questoes_simbolos_unicode'])}")
    print(f"  • Cabeçalho residual no texto: {len(r['questoes_cabecalho_residual'])}")
    print("-" * 50)
