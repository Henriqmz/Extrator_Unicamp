# Extrator_Unicamp

Trello: https://trello.com/b/ikVkMxb4/extrator-unicamp

Este projeto busca extrair todas as questões de provas do Vestibular UNICAMP (1ª e 2ª Fase) da edição de **2006 até 2026**. Se o gabarito oficial for fornecido, as alternativas corretas também serão indicadas de forma automática.

---

## 📦 Dependências do Projeto

O projeto utiliza Python 3.10+ e depende das seguintes bibliotecas e pacotes:

### 1. Núcleo de Extração e Processamento (Obrigatório)
* **`PyMuPDF` (`fitz`):** Leitura, análise geométrica de layout (colunas), extração de textos e dados vetoriais dos PDFs.
* **`Pillow` (`PIL`):** Processamento, recorte e conversão otimizada de imagens para o formato WebP.
* **`pydantic`:** Modelagem de dados tipada e validação estrita dos contratos de schema JSON.
* **`tkinter`:** Biblioteca nativa do Python para renderização da interface gráfica Desktop (`main.py`).

### 2. Módulo Opcional de Inteligência Artificial (Enriquecimento)
* **`google-genai`:** SDK oficial do Google Gemini para enriquecimento automático de matérias, assuntos, tópicos e resoluções.
* **`python-dotenv`:** Carregamento de credenciais locais (`GEMINI_API_KEY`) via arquivo `.env`.

### 3. Testes Automatizados
* **`pytest`:** Framework para execução da suíte formal de testes automatizados (`test_suite_pytest.py`).

### 💻 Como Instalar Todas as Dependências
Execute no terminal:
```bash
pip install pymupdf pillow pydantic google-genai python-dotenv pytest
```

---

## 📊 Formato de Saída (JSON Schema)

O extrator gera **1 arquivo JSON por questão**, estruturado da seguinte forma:

```json
{
  "metadados": {
    "codigo": "unicamp_2026_q1",
    "edital": "unicamp",
    "numero": 1,
    "tipo_ou_cor": "Q-X",
    "ano": 2026
  },
  "conteudo": {
    "enunciado": "Texto completo do enunciado da questão...",
    "url_img": ["imgs/unicamp_2026_q1_img_1.webp"],
    "dificuldade": null,
    "resolucao": null,
    "dica": null,
    "objetiva": true
  },
  "especificacao": {
    "disciplina": [],
    "assunto": [],
    "topicos": []
  },
  "alternativas": {
    "a": { "texto": "Alternativa A...", "url_img": [], "correta": false },
    "b": { "texto": "Alternativa B...", "url_img": [], "correta": true },
    "c": { "texto": "Alternativa C...", "url_img": [], "correta": false },
    "d": { "texto": "Alternativa D...", "url_img": [], "correta": false },
    "e": null
  }
}
```

---

## 📄 Textos Complementares de Apoio

Se a prova contiver um texto de apoio compartilhado entre múltiplas questões, um JSON complementar é gerado contendo:

```json
{
  "metadadosComp": {
    "codigos_questoes": ["1", "2"]
  },
  "conteudoComp": {
    "enunciado": "Texto complementar de apoio...",
    "img_url": "imgs/unicamp_2026_texto_comp_1.webp"
  }
}
```

---

## 🧪 Execução dos Testes Automatizados

O projeto possui suítes completas de testes unitários:

```bash
# Execução padrão via Runner nativo (57 testes)
python test_runner.py

# Execução formal via Pytest
python -m pytest -v test_suite_pytest.py
```

---

## 🚀 Suporte a Edições
- **Suporte Oficial Completo:** Vestibulares Unicamp da edição **2006 até 2026** (1ª Fase Objetiva/Discursiva e 2ª Fase Dissertativa por disciplinas).
