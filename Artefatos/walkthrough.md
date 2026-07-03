# Walkthrough: Correção na Extração de Questões Dissertativas (2ª Fase)

Este documento resume as correções aplicadas no parser de questões dissertativas de 2ª fase nas pastas `Projeto/` e `Projeto_API/`.

---

## 🛠️ Alterações Efetuadas

Foram implementadas as seguintes melhorias e correções para garantir a compatibilidade com provas dissertativas de todos os anos:

### 1. Robustez no Split das Questões (`processor.py`)
* **Regex para divisões de caixas de resolução**:
  Substituímos o split estático baseado em uma string rígida de caneta preta por uma expressão regular flexível:
  `r"Resolu[çc]\u00e3o\s+\(ser\u00e1\s+considerado\s+apenas\s+o\s+que\s+estiver\s+(?:escrito\s+com\s+caneta\s+(?:preta\s+)?)?dentro\s+deste\s+espa[çc]o\)\s*\.?\s*(?:RASCUNHO)?"`
  Isso permite processar provas de anos como 2021 (que não citavam "caneta" ou continham marcas como "RASCUNHO") e 2022 (que citavam apenas "caneta" em vez de "caneta preta").

### 2. Extração Dinâmica do Número de Questões
* **Fim do laço estático**:
  Removemos o limite fixo de 10 iterações na função `extrair_questoes_dissertativas`. O parser agora calcula dinamicamente a quantidade de questões presentes no caderno (`len(partes) - 1`), permitindo extrair corretamente as 22 questões presentes nas provas dissertativas de Ciências Exatas e Biológicas da Unicamp.

### 3. Melhoria na Detecção Automática de Tipo e Ano
* **Identificação de Prova de 2ª Fase**:
  Aprimoramos `detectar_edital_ano` para inspecionar tanto o nome do arquivo quanto o caminho da pasta em busca de palavras-chave como `exatas`, `biologicas`, `humanas` e `redacao`, configurando o tipo correto da prova (`EXATAS`, `BIOLOGICAS`, etc.) de forma robusta e evitando fallbacks indesejados para `Q-X`.

### 4. Acentuação em Cabeçalhos de Questões
* **Mapeamento de Imagens**:
  Ajustamos as expressões regulares de localização de questões (`localizar_questoes` e `mapear_imagens_a_questoes_e_alternativas`) para suportar acentuação e letras minúsculas em inícios de parágrafos (ex: `1. Água...`), evitando que imagens fiquem órfãs ou agrupadas sob uma única questão.

---

## 🧪 Verificação e Testes Realizados

1. **Prova de Exatas de 2022**:
   * Validamos manualmente a extração da prova `prova-exatas-tecnologicas.pdf` de 2022 com o script `scratch_test_2022.py`.
   * **Resultado**: 100% de sucesso (22 questões detectadas e extraídas corretamente sob o tipo `EXATAS`).

2. **Testes do Extrator Principal (`Projeto/`)**:
   * Executamos `test_runner.py` para garantir que as alterações não introduziram regressões.
   * **Resultado**: 57/57 testes PASS (Sucesso).

3. **Testes da API (`Projeto_API/`)**:
   * Executamos `test_api.py` para garantir que o comportamento da biblioteca permaneça estável e correto.
   * **Resultado**: 4/4 testes PASS (Sucesso).
