# AI Service Python

Projeto de portfólio para explorar uma API Python com FastAPI, validação de dados e testes automatizados. As funcionalidades disponíveis devem ser conferidas no código em `src/`; o repositório está em desenvolvimento e não representa, por si só, um serviço de IA pronto para produção.

## Stack

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- pytest

## Requisitos

Python 3.11 ou versão compatível com as dependências do projeto.

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

## Executar

Confira o ponto de entrada em `src/`. Se `src/main.py` expuser o objeto ASGI `app`, execute:

```bash
uvicorn src.main:app --reload
```

A documentação interativa do FastAPI normalmente fica em `/docs` quando a aplicação está em execução.

## Testes

```bash
pytest
```

## Estrutura

```text
.
├── src/
├── tests/
├── requirements.txt
└── README.md
```

## Boas práticas

- Não inclua tokens, chaves ou dados pessoais reais nos testes.
- Valide dados de entrada e padronize respostas de erro.
- Use testes para comportamento normal, entradas inválidas e falhas de dependências.
- Não apresente resultados de modelos como confiáveis sem avaliação com dados adequados.

## Próximas melhorias

- Documentar os endpoints reais e exemplos de requisição.
- Automatizar testes e verificações de estilo em CI.
- Adicionar configuração por variáveis de ambiente quando necessário.

Projeto em desenvolvimento; execute os testes antes de utilizar alterações em outros ambientes.
