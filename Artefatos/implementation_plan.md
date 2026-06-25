# Plano de Implementação: Suporte Global a 1ª/2ª Fase e API Desacoplada

Este plano propõe o desenvolvimento do suporte para a extração de provas de segunda fase (questões dissertativas) e a criação da biblioteca/API reutilizável. Incorporamos as decisões de design solicitadas:
1. **Interactive Prompt**: No `main.py`, o programa perguntará interativamente ao usuário qual fase ele deseja extrair (1ª ou 2ª), evitando erros de detecção automática.
2. **Design Limpo de Funções da API**:
   - Duas funções retornam apenas as questões em memória como uma lista (`List[Questao]`).
   - Duas funções realizam a extração e salvam os arquivos JSON diretamente no disco.
   - Parâmetro `caminho_gabarito` incluído para as funções da prova objetiva.

---

## Estrutura de Metadados Unificada (`models.py`)

Adicionamos a classe `SubItem` e tornamos `alternativas` opcional para dar suporte às duas fases de forma coerente:

```python
class SubItem(BaseModel):
    letra: str
    texto: str
    url_img: List[str] = []

class Questao(BaseModel):
    metadados: Metadados
    conteudo: Conteudo
    especificacao: Especificacao
    alternativas: Optional[Alternativas] = None  # Preenchido na 1ª fase (objetiva)
    sub_itens: Optional[List[SubItem]] = None    # Preenchido na 2ª fase (dissertativa)
```

---

## Modificações Propostas

### 1. Refatoração e Desenvolvimento em `Projeto/`

#### [MODIFY] [models.py](file:///C:/Users/henri/Desktop/Ike/Projeto/models.py)
* Criar a classe `SubItem` e alterar `Questao` para incluir `sub_itens` e tornar `alternativas` opcional.

#### [MODIFY] [processor.py](file:///C:/Users/henri/Desktop/Ike/Projeto/processor.py)
* Adicionar a função `extrair_questoes_dissertativas(texto, edital="unicamp", ano=2026, tipo_prova="Q-X")`:
  - Fazer o parsing de questões dissertativas de 2ª fase.
  - Identificar os cabeçalhos de questões (ex: `1. Leia...`, `2. Leia...`).
  - Separar o enunciado dos sub-itens `a)` e `b)`.
  - Mapear os sub-itens para objetos `SubItem`.
* Adaptar `mapear_imagens_a_questoes_e_alternativas` em `processor.py`:
  - Se a questão for dissertativa (campo `sub_itens` não estiver vazio), as imagens detectadas na página daquela questão serão associadas diretamente ao enunciado (`conteudo.url_img`), pois os sub-itens são discursivos.

#### [MODIFY] [main.py](file:///C:/Users/henri/Desktop/Ike/Projeto/main.py)
* Adicionar uma caixa de diálogo perguntando ao usuário:
  - *"Deseja extrair uma prova de 1ª Fase (Objetiva)? Se selecionar Não, prosseguiremos com a extração de 2ª Fase (Dissertativa)."*
* Direcionar o fluxo de processamento conforme a opção escolhida.

---

### 2. Criação da Pasta Reutilizável `Projeto_API/`

* Criar a pasta `Projeto_API/` no workspace.
* Copiar todos os módulos atualizados de `Projeto/` (`extractor.py`, `models.py`, `processor.py`, `saver.py`).
* **Criar o módulo de API (`api.py`)** expondo quatro funções explícitas:
  ```python
  # --- Funções de Extração em Memória ---
  
  def extrair_prova_objetiva(
      caminho_prova: str,
      caminho_gabarito: Optional[str] = None
  ) -> List[Questao]:
      """
      Extrai questões objetivas de múltipla escolha (1ª fase) e aplica gabarito (se fornecido).
      Retorna uma lista de objetos Questao em memória.
      """
      ...
      
  def extrair_prova_dissertativa(
      caminho_prova: str
  ) -> List[Questao]:
      """
      Extrai questões discursivas/dissertativas (2ª fase).
      Retorna uma lista de objetos Questao em memória.
      """
      ...
      
  # --- Funções de Extração e Gravação Direta ---
  
  def extrair_e_salvar_prova_objetiva(
      caminho_prova: str,
      pasta_destino: str,
      caminho_gabarito: Optional[str] = None
  ) -> None:
      """
      Extrai questões objetivas e textos complementares e os grava
      diretamente como arquivos JSON na pasta_destino indicada.
      """
      ...
      
  def extrair_e_salvar_prova_dissertativa(
      caminho_prova: str,
      pasta_destino: str
  ) -> None:
      """
      Extrai questões dissertativas e as grava diretamente
      como arquivos JSON na pasta_destino indicada.
      """
      ...
  ```
* **Adicionar Documentação (`README.md`)**:
  - Exemplos práticos demonstrando o uso de cada uma das 4 funções da API.

---

## Plano de Verificação

### Testes Automatizados em `Projeto/`
* Atualizar o `test_runner.py` para incluir a execução de teste da 2ª fase da prova de 2026 (`unicamp-2026-2-fase-prova-dia-1.pdf`).
* Validar as asserções de integridade do JSON gerado para as questões dissertativas.

### Testes Automatizados em `Projeto_API/`
* Criar `test_api.py` na pasta `Projeto_API/` para simular o uso da biblioteca:
  1. Chamar `extrair_prova_objetiva` e depois `extrair_prova_dissertativa`, asseverando a lista de retorno.
  2. Chamar `extrair_e_salvar_prova_objetiva` e `extrair_e_salvar_prova_dissertativa`, validando a criação física dos arquivos JSON e imagens.
