# Diretrizes e Regras do Pipeline de Extração Unicamp

Este documento consolida as regras técnicas e invariants desenvolvidos para o processamento de exames da Unicamp (1ª e 2ª Fase).

---

## 1. Tratamento de Expressões Regulares com Unicode
- Ao realizar pesquisas ou separações por expressão regular (`re.split`, `re.search`) sobre texto extraído do PDF em UTF-8:
  - Não utilizar raw strings (`r"..."`) contendo sequências de escape unicode (como `\u00e3`), pois elas são interpretadas como literais de barras e letras.
  - Usar os caracteres diretamente em UTF-8 (ex.: `Resolução`) ou strings padrão unescaped (`"Resolu[çc]\u00e3o"`).

## 2. Particionamento e Numeração de Provas Dissertativas (2ª Fase)
- Provas dissertativas divididas por disciplinas específicas (Exatas, Biológicas, Humanas) nem sempre iniciam a numeração em `1` (ex.: Humanas começa na Questão 10).
- O algoritmo de parsing deve extrair o número real indicado no cabeçalho (`(\d{1,2})\.`) e não forçar uma sequência fixa contada a partir de 1.
- Os delimitadores de folhas de resposta (`Resolução (será considerado apenas...)`) servem como ancoragem principal de separação de questões dissertativas.

## 3. Limpeza de Imagens e Isolamento de Cabeçalhos
- Ao calcular a bounding box de corte `m_padded` para salvar imagens WebP:
  - Garantir que a coordenada superior `m_padded.y0` respeite a borda inferior dos retângulos de cabeçalhos de questão (`headers_y1`) presentes na mesma coluna.
  - Isso impede a invasão da faixa cinza com o texto `QUESTÃO X` no topo das figuras extraídas.
