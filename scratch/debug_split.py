import re
from processor import extrair_questoes

texto = """QUESTÃO 65
No losango abaixo, qual é a medida do comprimento do segmento BE?
a)	26 	. c)	28 .
b)	27 . d)	29 .
QUESTÃO 66"""

questoes = extrair_questoes(texto)
print("TOTAL QUESTÕES EXTRAÍDAS:", len(questoes))
if questoes:
    q = questoes[0]
    print("ENUNCIADO:", repr(q.conteudo.enunciado))
    print("ALTERNATIVAS:")
    for letra in "abcd":
        alt = getattr(q.alternativas, letra)
        print(f"  {letra}: {repr(alt.texto) if alt else None}")
