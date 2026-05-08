from extractor import *
from processor import *
from saver import *
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def selecionar_pdf():
    Tk().withdraw()  # esconde a janela principal

    caminho = askopenfilename(
        title="Selecione o PDF",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )

    return caminho


# uso
pdf_path = selecionar_pdf()

if not pdf_path:
    print("Nenhum arquivo selecionado.")
else:
    print("Arquivo escolhido:", pdf_path)

# EXTRAÇÃO
paginas, doc = extrair_pdf(pdf_path)
texto = extrair_texto(paginas)
imagens = extrair_imagens(doc)

# PROCESSAMENTO
textos_comp = extrair_textos_comp(texto)
questoes = extrair_questoes(texto)

mapa_textos = mapear_textos_comp(textos_comp)
questoes_pos = localizar_questoes(paginas)
mapa_imgs = associar_imagens(questoes_pos, imagens)

questoes = enriquecer(questoes, mapa_textos, mapa_imgs)

# SALVAR
salvar_questoes(questoes)
salvar_textos(textos_comp)

print("Finalizado com sucesso 🚀")