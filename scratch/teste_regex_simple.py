import re

bloco = """QUESTÃO 65
No losango abaixo, qual é a medida do comprimento do segmento BE?
a)	26 	. c)	28 .
b)	27 . d)	29 ."""

bloco_processado = re.sub(r'(?<!\n)\s+\b([b-e])\)\s+', r'\n\1) ', bloco)
print("PROCESSADO:")
print(bloco_processado)
