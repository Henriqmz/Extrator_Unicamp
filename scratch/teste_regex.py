import re

bloco_q22 = """A parábola 𝑦= −𝑥2 + 𝑏𝑏+ 𝑐 intercepta o eixo 𝑥 nos pontos
(𝑝, 0) e (𝑞, 0). Sabe-se que ela intercepta uma única vez
cada uma das retas dadas pelas equações 𝑦= 2𝑥+ 1 e
𝑥
2. O valor de 𝑝+ 𝑞 é:
𝑦= 1 −
a) 2/3.                                    c) 4/3.
b) 3/4.                                    d) 3/2."""

bloco_processado = re.sub(r'(?<!\n)\s{2,}\b([b-e])\)\s+', r'\n\1) ', bloco_q22)
print("PROCESSADO:")
print(bloco_processado)

partes = re.split(r"\n\s*([a-e])\)\s*", bloco_processado)
print("\nPARTES:")
for i, p in enumerate(partes):
    print(f"Parte {i}: {repr(p)}")
