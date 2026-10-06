# Triagem de risco de recorrência em violência contra a pessoa idosa

Classificador que estima a probabilidade de uma notificação de violência contra pessoa idosa corresponder a caso recorrente, a partir dos microdados do SINAN/VIVA, para apoiar a priorização de atendimento em serviços de proteção.

- **Disciplina:** Planejamento e Gestão de Projetos
- **Tema:** Segurança Pública (violência contra a pessoa idosa)

## Análise e treinamento

Abra o notebook no Colab pelo link abaixo e execute as células em ordem. A única configuração necessária é o ano da base, na célula 3.

O notebook executa: download dos microdados, decodificação, filtro da população, análise exploratória, engenharia de atributos, treinamento, avaliação e exportação do modelo.

## Rodando modelo treinado localmente

```bash
cd app
python -m venv venv
venv\scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Testes

```bash
pytest -v
```

29 testes em três níveis: unitários (engenharia de atributos), integração (formulário → modelo) e aceite (carregamento e metadados).

---

## Links

| Recurso                           | Endereço                                                                              |
| --------------------------------- | ------------------------------------------------------------------------------------- |
| Aplicação publicada               | https://deploy-pgp.streamlit.app                                                      |
| Notebook de análise e treinamento | https://colab.research.google.com/drive/1WSgeGWBNRpLxTwzIUeCjchNx_RDx7QcZ?usp=sharing |
| Artigo científico                 | https://www.overleaf.com/project/6a98970e73b7c7c4936031d9                             |

## Dados

**Fonte:** Microdados do SINAN/VIVA, Violência Interpessoal e Autoprovocada, Ministério da Saúde, ano de 2024. Obtidos do servidor FTP público do DATASUS.

**Dicionário:** Dicionário de Dados do SINAN NET, versão 5.0 / Patch 5.1 (SVS/GT-SINAN, revisado em junho de 2015).

### Recorte da população

| Etapa                                              | Registros     |
| -------------------------------------------------- | ------------- |
| Notificações de violência no ano (todas as idades) | 616.548       |
| Vítimas com 60 anos ou mais                        | 42.176 (6,8%) |
| Após exclusão da violência autoprovocada           | 35.129        |
| Com variável-alvo preenchida                       | 25.056        |
| Após remoção de duplicatas                         | 24.017        |

A violência autoprovocada (16,7% dos registros) foi excluída por constituir fenômeno distinto, com dinâmica de recorrência própria.

---

## Resultados

### Comparação de modelos

| Modelo                       | AUC teste | AUC CV | DP CV | Acurácia | Recall | Precisão |
| ---------------------------- | --------- | ------ | ----- | -------- | ------ | -------- |
| **HistGradientBoosting**     | **0,836** | 0,837  | 0,005 | 0,758    | 0,810  | 0,762    |
| Random Forest                | 0,830     | 0,834  | 0,004 | 0,760    | 0,836  | 0,752    |
| Regressão logística          | 0,825     | 0,825  | 0,002 | 0,751    | 0,813  | 0,751    |
| Baseline (_DummyClassifier_) | 0,500     | 0,500  | 0,000 | 0,546    | 1,000  | 0,546    |

> Obs: o recall de 1,000 do baseline não indica desempenho.

### Testes de robustez

| Teste                       | Resultado                                                     |
| --------------------------- | ------------------------------------------------------------- |
| Alvo embaralhado            | AUC 0,498 — sem vazamento de dado                             |
| Estabilidade entre sementes | 0,840 a 0,004 em 5 divisões distintas                         |
| Calibração                  | Aderência à diagonal em 10 faixas, desvio máximo de 6 p.p.    |
| Remoção de duplicatas       | Queda de 0,010 na AUC — desempenho não decorre de memorização |

## Limitações

**Viés de seleção.** A base contém apenas casos notificados. Pessoas idosas isoladas, acamadas ou sem acesso a serviços não figuram nela, de modo que o modelo tende a subestimar o risco nos perfis mais vulneráveis. O sistema prioriza casos registrados; não identifica violência não notificada.

**Variável-proxy.** A recorrência é usada como substituta de risco de dano futuro, por indisponibilidade de medida direta de gravidade nos microdados.

**Ausência não aleatória.** Foram excluídos 28,7% dos registros por preenchimento ausente da variável-alvo. A ausência pode correlacionar-se ao próprio valor, já que o registro depende de a informação ter sido levantada no atendimento.

**Qualidade do instrumento.** A exploração identificou 13,9% de registros sem identificação de autoria, em campo de preenchimento obrigatório, e 4,2% de contradição entre campos que descrevem o mesmo fato.

## Equipe

- _Nicole Moritz_
- _Morgane de Avila_
