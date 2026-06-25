# Tarefas de Execução: Suporte Global a 1ª e 2ª Fase e API Isolada

Este documento rastreia o progresso do desenvolvimento do suporte para a extração de provas de segunda fase (questões dissertativas) e a criação da interface de API com funções de alto nível independentes de gravação.

## Checklist de Implementação

- `[x]` **Fase 1: Refatoração da Pasta `Projeto/` (Suporte 2ª Fase)**
  - `[x]` Adicionar `SubItem` em [models.py](file:///C:/Users/henri/Desktop/Ike/Projeto/models.py) e atualizar `Questao` com `sub_itens` opcional.
  - `[x]` Implementar `extrair_questoes_dissertativas` em [processor.py](file:///C:/Users/henri/Desktop/Ike/Projeto/processor.py).
  - `[x]` Adaptar o mapeamento de imagens e o `main.py` de `Projeto/` para usar o prompt interativo para escolha da fase da prova.
  - `[x]` Adicionar cobertura de testes para a 2ª fase no `test_runner.py` original.

- `[x]` **Fase 2: Configuração e Cópia para a Pasta `Projeto_API/`**
  - `[x]` Criar a nova pasta `Projeto_API` no workspace.
  - `[x]` Copiar todos os módulos refatorados de `Projeto/` para `Projeto_API/`.
  - `[x]` Criar o módulo principal `api.py` na nova pasta expondo 4 funções: `extrair_prova_objetiva`, `extrair_prova_dissertativa`, `extrair_e_salvar_prova_objetiva` e `extrair_e_salvar_prova_dissertativa` (com os devidos parâmetros de gabarito e diretórios).

- `[x]` **Fase 3: Verificação e Testes da API**
  - `[x]` Criar o script [test_api.py](file:///C:/Users/henri/Desktop/Ike/Projeto_API/test_api.py) na pasta `Projeto_API/`.
  - `[x]` Validar a extração em memória (`List[Questao]`) para ambas as fases.
  - `[x]` Validar a gravação direta em disco (`extrair_e_salvar...`) para ambas as fases.
  - `[x]` Garantir que 100% dos testes passam em ambas as pastas.
