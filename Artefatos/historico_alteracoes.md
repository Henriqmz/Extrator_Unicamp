# Histórico de Alterações (Changelog)

Este documento registra todas as alterações feitas no Extrator de Provas e no Guia de Estudos, bem como decisões de design tomadas ao longo do projeto.

---

## [2026-06-18] Sessão de Metadados e API (ID: 56629adb-9887-473c-8214-0163c6f0a2a7)

### Refatoração da Classificação de Questões e Arquitetura de Biblioteca
* **Nova Estrutura de Metadados**: Substituição definitiva de `materia` e `tags` em `models.py` por:
  - `area` (string): Para separar áreas macro (ex: "Exatas", "Linguagens", "Humanas").
  - `disciplina` (List[str]): Lista de matérias para acomodar multidisciplinaridade (ex: `["Matemática"]`).
  - `assunto` (List[str]): Lista de temas de estudo abordados (ex: `["Geometria"]`).
  - `topico` (List[str]): Lista de conceitos específicos (ex: `["Teorema de Pitágoras"]`).
* **Adaptação no Processamento (`processor.py`)**:
  - `extrair_questoes` agora inicializa `Especificacao` com os novos campos e listas vazias.
  - Atualização do prompt e do loop de parsing em `enriquecer_questoes_com_ia` para manter a compatibilidade do Gemini com as novas propriedades de lista, incluindo higienização via blacklist.
* **Isolamento de IA nos Testes**:
  - Conforme solicitado pelo usuário, desativamos o uso da IA no pipeline de validação automatizada (`enrich_ia=False` em `test_runner.py`), garantindo que os novos campos permaneçam inicializados como vazios durante os testes de integridade local.
* **Correções de Codificação e Caminhos**:
  - Ajustada a suíte de testes `test_runner.py` para usar tabelas ASCII simples no console, prevenindo erros de codificação de caracteres Unicode (`UnicodeEncodeError`) no prompt de comando CP1252 do Windows.
  - Recuperado e organizado o diretório `Provas` a partir do zip fornecido, corrigindo caminhos e nomes de arquivos das edições de 2025 (`caderno-provas-Q-Z-vestibular-2025-unicamp.pdf` e seu gabarito) para viabilizar 100% de cobertura nos testes.
* **Validação Geral**: Executado com sucesso o test runner confirmando que todos os 55 testes passam na máquina local.

---

## [2026-06-18] Sessão de Provas da 2ª Fase e API Isolada (ID: 56629adb-9887-473c-8214-0163c6f0a2a7)

### Implementação da 2ª Fase (Dissertativa) e Interface da API
* **Modelo Pydantic Estendido (`models.py`)**:
  - Adicionada a classe `SubItem` (`letra: str`, `texto: str`, `url_img: List[str]`).
  - Atualizada a classe `Questao` para aceitar `sub_itens` como opcional e tornar `alternativas` opcional (já que questões dissertativas não têm múltipla escolha).
* **Mecanismo de Parsing Dissertativo (`processor.py`)**:
  - Implementada a função `extrair_questoes_dissertativas` em `processor.py` baseada em split por cabeçalho de página (`Resolução (será considerado apenas o que estiver escrito...)`), com regex de identificação sequencial de sub-itens (`a)` e `b)`).
  - Atualizadas as funções de enriquecimento e mapeamento de imagens para lidar graciosamente com a ausência de alternativas e atribuir as imagens da página ao enunciado da questão discursiva.
* **Escolha Interativa da Fase da Prova (`main.py`)**:
  - Substituída a tentativa de detecção de fase automática para evitar erros. Agora a GUI (Tkinter pop-up) pergunta interativamente ao usuário se a prova selecionada é de 1ª Fase (Objetiva) ou 2ª Fase (Dissertativa).
* **Criação da API Separada (`Projeto_API/`)**:
  - Criada uma pasta `Projeto_API` dedicada e limpa no workspace contendo apenas as bibliotecas essenciais (`extractor.py`, `models.py`, `processor.py`, `saver.py`).
  - Criado o arquivo `api.py` expondo 4 funções de alto nível: `extrair_prova_objetiva`, `extrair_prova_dissertativa`, `extrair_e_salvar_prova_objetiva` e `extrair_e_salvar_prova_dissertativa`.
  - Criado o arquivo `test_api.py` na pasta da API, validando com sucesso a extração das duas fases (tanto em memória quanto gravando em disco).
  - Criado o `README.md` com instruções detalhadas de importação, uso e dependências.
* **Validação dos Testes**:
  - Execução bem-sucedida da suíte geral no `Projeto/` (`test_runner.py`), totalizando 57/57 PASS.
  - Execução bem-sucedida da suíte da API em `Projeto_API/` (`test_api.py`), totalizando 4/4 PASS.

---

## [2026-05-21] Sessão Atual (ID: 527455db-c0aa-4e79-aaf5-55f6cdb25b95)

### Início dos Trabalhos: Integração e Refatoração Completa
* **Objetivo Geral**: Executar o planejamento da última conversa (`f4033a32-68d8-4095-a85f-ece7261b9e76`), dando continuidade ao plano de estudos da primeira conversa (`9b21ec99-b59d-477b-8607-c0601aa45b72`/`042b1f7d-5511-4696-8e90-a741eaf93f34`).
* **Novidade/Alteração Solicitada**: Ajustar o mecanismo de estimativa de tempo do enriquecimento via IA. O tempo total restante passa a ser estimado com base no tempo real decorrido da **primeira requisição à API**, multiplicado pela quantidade de requisições restantes (levando em conta também a pausa obrigatória de 4.5 segundos).
* **Estrutura dos Arquivos**:
  * Importação e criação do Guia de Estudos local (`guia_estudo.md`).
  * Criação do registro de alterações (`historico_alteracoes.md`).

---

## [2026-05-21] Sessão Atual (ID: 56629adb-9887-473c-8214-0163c6f0a2a7)

### Conclusão e Consolidação do Plano de Implementação
* **Migração Definitiva para a Raiz**: Todos os módulos otimizados (`extractor.py`, `models.py`, `processor.py`, `saver.py`, `main.py`, `test_runner.py`) foram consolidados na raiz do workspace, eliminando a redundância da pasta `Teste/`.
* **Limpeza Completa do Workspace (Declutter)**: Exclusão total da pasta `Teste/`, do arquivo temporário `texto para o gemini.txt`, e de diretórios órfãos na raiz.
* **Processamento Otimizado em Lotes de 20**: Conforme sugestão aprovada pelo usuário, o agrupamento foi configurado para lotes de exatamente 20 questões por requisição (`tamanho_lote = 20`), maximizando o aproveitamento do contexto e reduzindo os custos de chamadas de API em 95%.
* **Espaçamento e Estimativa de Tempo Dinâmicos (Pacing Inteligente)**: O intervalo de 4,5 segundos para respeitar o limite de 15 RPM foi tornado dinâmico. O script agora calcula o tempo decorrido desde o início da chamada anterior e dorme apenas a diferença necessária para atingir 4,5s (sendo zerado se a própria chamada síncrona demorar mais de 4,5s, o que é o padrão). A projeção do tempo restante foi atualizada para `lotes_restantes * max(tempo_primeira_req, 4.5)`. Os avisos de log no console também foram atualizados para refletir essa alteração precisa.
* **Dupla Defesa (Double-Defense) de Tags**:
  - Filtro programático complementar nativo em Python (`TAG_BLACKLIST` com termos como *unicamp*, *física*, *matemática*, etc.) para barrar tags genéricas.
  - Alinhamento rigoroso nas diretivas do prompt do Gemini para retornar exclusivamente tópicos teóricos (ex: *Termodinâmica*, *Citologia*).
* **Manutenção de Enunciados Limpos**: O texto complementar de apoio é injetado dinamicamente apenas na chamada de IA e não é gravado fisicamente dentro do enunciado da questão no JSON, mantendo a integridade original dos dados.
* **Persistência Windows-Compatible e Nomes Limpos**: O módulo `saver.py` foi ajustado para substituir caracteres proibidos no Windows (como `/` em `"Q/X"`) por hífen `-`, salvar diretamente nas subpastas dinâmicas correspondentes (`{edital}_{ano}/`), e adotar o nome limpo simplificado para os textos complementares: `{edital}_{ano}_{tipo_ou_cor_limpo}_COMP_{idx}.json` (sem o prefixo redundante "Texto Complementar").
* **Validação de Sucesso**: Executado com êxito o `test_runner.py` usando o interpretador correto, validando a extração impecável de 72 questões, 3 textos complementares e 57 imagens da prova Unicamp 2026.
* **Portabilidade de Imagens (Caminhos Relativos)**: Implementação de caminhos de imagem 100% relativos (`./imgs/...` em vez de `unicamp_2026/imgs/...`) no JSON (`url_img`) e nas referências markdown dos enunciados (`![figura]`), tornando a pasta de saída do vestibular totalmente autônoma e portátil.
* **Segurança e Versionamento (`.gitignore`)**: Criação do arquivo `.gitignore` na raiz para impedir o rastreamento acidental do arquivo sensível `.env` (contendo a chave do Gemini), compilados de Python (`__pycache__`) e arquivos temporários no GitHub.
* **Melhorias de Usabilidade e UX Gráfica (`main.py`)**:
  - Exibição de aviso popup informativo orientando o usuário antes de abrir a janela de seleção do PDF.
  - Pergunta explícita via popup Sim/Não para autorizar o enriquecimento das questões com IA.
  - Se a IA for selecionada mas nenhuma chave Gemini for encontrada no `.env`, o programa apresenta um tutorial passo-a-passo e confirmação, recarregando dinamicamente o arquivo `.env` caso o usuário conclua as instruções no momento.
  - **Correção de Usabilidade da IA Gráfica**: Corrigido um bug crítico de recuo (indentação) no qual o fluxo de enriquecimento da IA estava acidentalmente aninhado no bloco `except` de tratamento de erro do Gabarito. Isso fazia com que a interface nunca solicitasse o enriquecimento por IA quando o fluxo de gabarito terminava com sucesso. O bloco foi movido para o nível do módulo e agora funciona perfeitamente.
* **Atualização dos Artefatos de Estudo**:
  - Guia de Estudos (`guia_estudo.md`) estendido para explicar o processamento em lote de 20, dupla defesa de tags, estimativa de tempo dinâmica e caminhos portáveis relativos de imagens.
  - Registro de Alterações (`historico_alteracoes.md`) atualizado para documentar cada evolução do código nesta sessão.
* **Padronização de Nomenclatura**: O usuário removeu manualmente o prefixo `"Questões-"` dos arquivos gerados (`saver.py`). O `test_runner.py` foi atualizado para alinhar sua verificação automática a essa nova regra, identificando e testando as questões corretamente sem o prefixo.
* **Nomenclatura Única de Imagens**: Implementação de nomenclatura exclusiva para imagens extraídas em `extractor.py`, aplicando o prefixo do vestibular `{edital}_{ano}_{tipo_prova}_` (ex: `unicamp_2026_Q-X_p2_img0.jpeg`). Isso evita colisões de nomes caso imagens de provas ou edições diferentes sejam reunidas no mesmo repositório, mantendo a compatibilidade automática com a associação de questões no JSON e Markdown.
* **Lista de Imagens em `url_img`**: Alterado o esquema da propriedade `url_img` nos modelos Pydantic (`Conteudo` e `AlternativaItem`) de `Optional[str]` para uma lista de strings (`List[str]`). Ajustada a função `enriquecer` em `processor.py` para mapear todos os recursos gráficos (imagens e desenhos vetoriais) associados a uma mesma questão na lista (em vez de reter apenas a primeira), e adaptado o `test_runner.py` para reportar essa lista de forma legível.
* **Associação Robusta de Imagens via Regex (Column-Proof)**: Em vez de realizar uma associação geométrica baseada em coordenadas `y` brutas (que falha em páginas com duas colunas), implementamos uma extração por Regex (`re.findall`) diretamente no texto do enunciado e das alternativas de cada questão. Como o motor `extrair_texto` já insere as referências markdown `![figura](...)` respeitando a divisão inteligente de colunas, conseguimos extrair as imagens de forma 100% fiel e sem falsos-positivos de outras questões.

