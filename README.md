# AI Service Python

Módulo Python experimental para análise básica de texto e processamento em lote. Apesar de FastAPI e Uvicorn estarem listados nas dependências, o ponto de entrada atual `src/main.py` é uma biblioteca/exemplo executável por terminal, não uma aplicação FastAPI pronta.

## Funcionalidades atuais

- Rejeita texto vazio.
- Remove espaços externos.
- Conta palavras.
- Estima sentimento por um pequeno léxico positivo/negativo em inglês e português.
- Considera negações simples (`not`, `never`, `não`, `nao`, `nunca`) e contrações comuns em inglês (`don't`, `isn't`, `can't`) em uma janela curta e reinicia o escopo em pontuação ou conectores de contraste.
- Informa um escore heurístico (`confidence`) e o método usado; esse escore não é uma probabilidade calibrada.
- Processa uma lista de textos, ignorando itens vazios. Cada texto pode ter até **10.000 caracteres** e cada lote pode conter até **100 itens**, para limitar o trabalho por chamada.

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
