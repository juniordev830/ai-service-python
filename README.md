# AI Service Python

Módulo Python experimental para análise básica de texto e processamento em lote. O ponto de entrada `src/main.py` é uma biblioteca/exemplo executável por terminal. O analisador usa apenas a biblioteca padrão; `requirements.txt` contém a dependência de testes.

## Funcionalidades atuais

- Rejeita texto vazio.
- Remove espaços externos.
- Conta palavras.
- Estima sentimento por um pequeno léxico positivo/negativo em inglês e português.
- Trata acentos Unicode compostos e decompostos de forma equivalente, preservando o texto original na resposta (exceto espaços externos).
- Considera negações simples (`not`, `never`, `não`, `nao`, `nunca`) e contrações comuns em inglês (`don't`, `isn't`, `can't`) em uma janela curta e reinicia o escopo em pontuação ou conectores de contraste.
- Informa um escore heurístico (`confidence`) e o método usado; esse escore não é uma probabilidade calibrada.
- Processa uma lista de textos, ignorando itens vazios. Cada texto pode ter até **10.000 caracteres** e cada lote pode conter até **100 itens**, para limitar o trabalho por chamada.

O limite de caracteres é conferido na entrada original, inclusive em itens
compostos apenas por espaços, antes de ignorá-los ou normalizar seus acentos.

> O rótulo de sentimento e a confiança são regras didáticas, não previsões de um modelo de Machine Learning validado. Não use os resultados para decisões reais.

## Requisitos

- Python 3.11+ recomendado
- Dependências em `requirements.txt`

## Instalação

```bash
python -m venv .venv
```

Ative o ambiente:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

## Executar o exemplo

```bash
python src/main.py
```

## Testes

```bash
pytest
```

## Estrutura

```text
.
├── src/main.py
├── tests/
├── requirements.txt
└── README.md
```

## Próximas melhorias

- Ampliar e versionar o léxico e melhorar o tratamento de expressões, ironia, negações compostas e conectores de contraste.
- Adicionar testes para entrada vazia, espaços, texto curto e lote misto.
- Se for necessário expor HTTP, criar uma aplicação FastAPI explícita com schemas Pydantic e documentação dos endpoints.
- Substituir as heurísticas por um método avaliado e documentar métricas antes de chamá-lo de modelo de IA.

Projeto de aprendizagem em evolução.


## Relatório agregado de textos (novo)

O comando `src.report` recebe uma **lista JSON de strings** em UTF-8 e produz um resumo com quantidades de rótulos positivo/negativo/neutro, textos vazios ignorados e total de palavras.

```bash
python -m src.report examples/textos.json
python -m pytest tests/test_report.py -q
```

A saída é um objeto JSON. Por padrão, **o relatório não reproduz os textos originais**, ajudando a reduzir exposição acidental ao compartilhar estatísticas. O arquivo de entrada precisa existir localmente, ter no máximo 2 MB, conter no máximo 100 entradas e cada texto precisa respeitar o limite do analisador (10.000 caracteres).

O método continua sendo uma **heurística de léxico**, não um modelo de linguagem treinado nem uma classificação confiável para decisões importantes. O programa não recebe dados pela rede e não persiste relatórios automaticamente. Ao usar exemplos próprios, evite dados pessoais ou confidenciais.

### Comparar dois lotes

```bash
python -m src.report examples/textos.json --baseline lote-anterior.json
```

`--baseline` compara o lote atual com outro arquivo JSON no mesmo formato.
A saída inclui os dois resumos e, para cada sentimento, a diferença de contagem,
os percentuais de cada lote e a variação em **pontos percentuais** (atual menos
anterior). Textos vazios não entram no denominador. Sem textos analisados em
um dos lotes, seu percentual e a variação são `null`, pois não há taxa a comparar.
Os percentuais são arredondados para duas casas e podem não somar exatamente 100.
Cada arquivo conserva os limites de tamanho e quantidade do relatório simples.
Nenhum texto original é incluído; as variações são descritivas, sem indicar
significância estatística ou melhora de qualidade. Sem `--baseline`, a saída
original do relatório permanece a mesma.
