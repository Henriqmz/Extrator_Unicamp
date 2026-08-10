# Extrator_Unicamp

Trello: https://trello.com/b/ikVkMxb4/extrator-unicamp

Este projeto busca extrair todas as questões de provas do Vestibular UNICAMP (1ª e 2ª Fase) da edição de **2006 até 2026**. Se o gabarito oficial for fornecido, as alternativas corretas também serão indicadas de forma automática.

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

### 🚀 Suporte a Edições
- **Suporte Oficial Completo:** Vestibulares Unicamp da edição **2006 até 2026** (1ª Fase Objetiva/Discursiva e 2ª Fase Dissertativa por disciplinas).
