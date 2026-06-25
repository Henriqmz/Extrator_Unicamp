# Walkthrough: Suporte Global a 2ª Fase e API Isolada

Este documento resume a conclusão de todas as etapas de desenvolvimento do suporte para a extração de provas de segunda fase (questões dissertativas) e a criação da interface de API isolada com funções programáticas de alto nível.

---

## 🛠️ Alterações Efetuadas

Todas as modificações foram consolidadas com sucesso diretamente no workspace:

### 1. Suporte a Questões Dissertativas (2ª Fase) na pasta `Projeto/`
* **Schema de Dados (`models.py`)**:
  - Introdução do modelo `SubItem` (`letra: str`, `texto: str`, `url_img: List[str]`).
  - Atualização do modelo `Questao` para conter `sub_itens: Optional[List[SubItem]]` (para discursivas) e tornar `alternativas` opcional (pois discursivas não possuem alternativas de múltipla escolha).
* **Mecanismo de Extração (`processor.py`)**:
  - Implementação de `extrair_questoes_dissertativas` baseada em quebra por cabeçalho de página, uma vez que na Unicamp cada questão discursiva ocupa exatamente uma página, e o bloco de enunciado e a área de resolução aparecem em ordem sequencial.
  - Salvaguardas aplicadas nas rotinas de mapeamento de imagens e textos complementares para aceitarem `alternativas=None` e atribuírem imagens de forma precisa ao enunciado de questões dissertativas.
* **Interface Interativa (`main.py`)**:
  - Removida a tentativa de detecção automática da fase da prova por PDF, que poderia induzir a erros.
  - Implementada uma tela de diálogo (Tkinter GUI pop-up) que explicitamente pergunta ao usuário se a prova selecionada é de 1ª Fase (Objetiva) ou de 2ª Fase (Dissertativa). A extração prossegue conforme a seleção.
* **Cobertura de Testes (`test_runner.py`)**:
  - Configurado o caminho da prova de 2ª fase de 2026.
  - Inclusão dos testes `D01` (quantidade de questões discursivas) e `D02` (estrutura e conteúdo dos sub-itens da Q1) na suíte principal.

### 2. Criação do Módulo Programático `Projeto_API/`
Criamos uma pasta totalmente nova e isolada no workspace contendo o código necessário para uso como biblioteca independente por outros desenvolvedores.
* **Módulos Copiados**: `extractor.py`, `models.py`, `processor.py` e `saver.py`.
* **Módulo de Interface (`api.py`)**:
  Implementa e expõe exatamente 4 funções públicas de alto nível:
  1. `extrair_prova_objetiva(caminho_prova, caminho_gabarito=None) -> List[Questao]`
  2. `extrair_prova_dissertativa(caminho_prova) -> List[Questao]`
  3. `extrair_e_salvar_prova_objetiva(caminho_prova, pasta_destino, caminho_gabarito=None) -> None`
  4. `extrair_e_salvar_prova_dissertativa(caminho_prova, pasta_destino) -> None`
* **Documentação (`README.md`)**:
  Explica claramente como instalar requisitos, realizar as importações e invocar cada função com exemplos de uso.
* **Script de Testes (`test_api.py`)**:
  Roda validações automatizadas em memória e em disco para ambas as fases da prova de 2026, garantindo a integridade e precisão dos dados retornados.

---

## 🧪 O que foi Testado e Resultados

### 1. Suíte de Testes Geral (`Projeto/`)
A suíte foi executada e passou com **100% de sucesso**:
```powershell
& "C:\Python314\python.exe" test_runner.py
```
* **Total de Testes**: 57/57 PASS (incluindo testes `D01` e `D02`).
* **Falhas**: 0.

### 2. Suíte de Testes da API (`Projeto_API/`)
A nova API foi validada localmente com sucesso:
```powershell
& "C:\Python314\python.exe" test_api.py
```
* **Total de Testes**: 4/4 PASS (validação de extração objetiva/dissertativa em memória e em disco).
* **Falhas**: 0.
