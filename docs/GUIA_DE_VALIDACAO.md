# Guia de manutenção — AI Service Python

## Escopo confirmado

Serviço experimental de análise textual e relatórios locais com léxico heurístico, não modelo treinado de produção.

## Arquivos principais

`src/main.py`, `src/report.py`, `tests/test_main.py`, `tests/test_comparison.py` e `tests/test_csv_report.py`.

## Validar uma alteração

No diretório raiz, usar os comandos adequados ao ambiente: `python -m pip install -r requirements.txt` e `python -m pytest tests -q`.

Registrar o resultado dos testes no PR e conferir se a execução do GitHub Actions corresponde ao commit revisado. Não presumir que a interface ou o serviço é de produção apenas porque o build passou.

## Revisão de casos críticos

Verificar textos vazios, negações, acentos decompostos, frases mistas e exportação CSV com caracteres de fórmula; registrar casos de falso positivo/negativo.

## Limites e próxima entrega

O escore não representa probabilidade calibrada. Próxima etapa: ampliar corpus sintético de regressão, separar decisões linguísticas de formatação e medir precisão.

### Checklist para PR

- [ ] A mudança está associada a um comportamento identificável.
- [ ] Foram documentados os casos novos e os limites encontrados.
- [ ] Há teste automatizado quando o módulo comporta execução reproduzível.
- [ ] Exemplos não contêm credenciais ou dados reais.
- [ ] A branch pode ser revisada antes de qualquer merge na principal.
