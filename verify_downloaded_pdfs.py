import os
import fitz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROVAS_DIR = os.path.join(BASE_DIR, "Provas")

total_inspected = 0
valid_pdfs = 0
errors = []

for root, dirs, files in os.walk(PROVAS_DIR):
    for f in files:
        if f.lower().endswith('.pdf'):
            total_inspected += 1
            path = os.path.join(root, f)
            size = os.path.getsize(path)
            if size == 0:
                errors.append(f"Arquivo vazio (0 bytes): {path}")
                continue
            try:
                with open(path, 'rb') as fp:
                    header = fp.read(5)
                    if header != b'%PDF-':
                        errors.append(f"Cabeçalho inválido ({header}): {path}")
                        continue
                with fitz.open(path) as doc:
                    if doc.page_count == 0:
                        errors.append(f"Sem páginas: {path}")
                        continue
                valid_pdfs += 1
            except Exception as e:
                errors.append(f"Erro ao abrir {path}: {e}")

print("=" * 60)
print(f"VERIFICAÇÃO DE INTEGRIDADE DOS PDFs:")
print(f"  Total de PDFs inspecionados: {total_inspected}")
print(f"  PDFs válidos e íntegros: {valid_pdfs}")
print(f"  Erros encontrados: {len(errors)}")
print("=" * 60)
if errors:
    for err in errors[:10]:
        print("  -", err)
else:
    print("TODOS OS PDFs ESTÃO 100% ÍNTEGROS E VÁLIDOS!")
