---
name: batch-exam-extraction-audit
description: >-
  Skill para execução em lote do pipeline de extração de exames vestibulares
  (1ª Fase objetiva e 2ª Fase dissertativa) e auditoria automatizada de qualidade estrutural,
  integridade visual das imagens WebP e análise comparativa ano a ano.
---

# Skill: Execução e Auditoria em Lote de Provas (Batch Exam Extraction & Audit)

Esta skill define o procedimento padrão para executar o pipeline de extração em lote sobre múltiplos PDFs de provas (objetivas e dissertativas) e realizar a auditoria completa de qualidade, integridade visual e comparação estatística dos dados extraídos.

---

## Workflow de Execução

### 1. Preparação e Mapeamento dos PDFs
Ao executar o pipeline em lote para múltiplos anos (ex.: 2022 a 2026):
1. Mapeie dinamicamente os caminhos dos PDFs de prova e gabarito na pasta `Provas/` usando busca por padrões glob (`*prova-*.pdf`, `*gabarito-*.pdf`).
2. Identifique o tipo da prova (objetiva 1ª fase vs dissertativa 2ª fase).
3. Defina a pasta de saída estruturada (ex.: `exec_results/{ano}_{fase}_{tipo}`).

### 2. Execução da Extração
Rode o script em lote `scripts/run_batch_extraction.py` no ambiente Python da aplicação:
```bash
python .agents/skills/batch-exam-extraction-audit/scripts/run_batch_extraction.py
```
O script realizará:
- Leitura e particionamento do PDF (páginas, imagens visuais).
- Chamada do extrator de questões objetivas (`extrair_questoes`) ou dissertativas (`extrair_questoes_dissertativas`).
- Mapeamento dinâmico de textos complementares e vinculação de imagens WebP.
- Aplicação de gabaritos oficiais onde disponíveis.
- Salvamento dos JSONs individuais de questões e relatório sumário `resumo_execucao.json`.

---

## Workflow de Auditoria e Qualidade

Após o processamento dos lotes, execute a suíte de análise de qualidade:
```bash
python .agents/skills/batch-exam-extraction-audit/scripts/analyzer_agent.py
```

### Verificações Automatizadas da Auditoria:
1. **Integridade de Imagens WebP (`imagens_quebradas`):**
   - Confirma se todas as referências de imagem nos arrays `url_img` apontam para arquivos `.webp` existentes no disco com tamanho válido (> 50 bytes).
2. **Sanitização de Enunciados (`questoes_cabecalho_residual`):**
   - Verifica se não há resíduos de tarjas ou delimitadores `QUESTÃO X` misturados ao texto do enunciado.
3. **Detecção de Notação Matemática (`questoes_simbolos_unicode`):**
   - Inspeciona se houve falhas de extração de fontes em fórmulas matemáticas que geraram caracteres unicode corrompidos.
4. **Verificação de Quantidade e Cobertura:**
   - Valida se o total de questões extraídas por caderno bate com a estrutura oficial (ex.: 72 para 1ª Fase; 10 a 22 para 2ª Fase).

---

## Estrutura de Arquivos da Skill

- `SKILL.md`: Guia e instrução do fluxo de trabalho.
- `scripts/run_batch_extraction.py`: Script Python executável para processar exames em lote.
- `scripts/analyzer_agent.py`: Script Python executável para auditoria de integridade e qualidade.
