# Lab05 - GraphQL vs REST: Um Experimento Controlado

## Descrição

Trabalho desenvolvido para comparar quantitativamente as APIs GraphQL e REST. O objetivo é medir o tempo de resposta e o tamanho das respostas em diferentes cenários de uso.

## Estrutura do Projeto

```
lab05/
├── experimento_desenho.md      # Desenho completo do experimento
├── backend/
│   ├── rest/                   # Implementação da API REST
│   ├── graphql/                # Implementação da API GraphQL
│   └── shared/                 # Código compartilhado (database, models)
├── scripts/
│   ├── setup_database.py      # Script para criar dataset sintético
│   ├── benchmark.py           # Script principal de medição
│   └── analyze_results.py     # Script para análise estatística
├── results/                    # Resultados das medições (CSV/JSON)
├── dashboard/                  # Código para visualização (Sprint 2)
└── requirements.txt            # Dependências Python
```

## Perguntas de Pesquisa

- **RQ1**: Respostas às consultas GraphQL são mais rápidas que respostas às consultas REST?
- **RQ2**: Respostas às consultas GraphQL têm tamanho menor que respostas às consultas REST?

## Sprint 1 - Objetivos

- [x] Desenho do experimento
- [x] Preparação do experimento (APIs e scripts de medição)

## Requisitos

- Python 3.8+
- Node.js 16+
- npm ou yarn

## Instalação

### Python (para scripts de medição)

```bash
# No macOS/Linux, use:
python3 -m pip install -r requirements.txt
# ou
pip3 install -r requirements.txt
```

### Node.js (para APIs)

```bash
cd backend/rest
npm install

cd ../graphql
npm install
```

## Execução

### 1. Criar dataset sintético

```bash
python scripts/setup_database.py
```

### 2. Iniciar APIs

Terminal 1 - API REST:
```bash
cd backend/rest
npm start
```

Terminal 2 - API GraphQL:
```bash
cd backend/graphql
npm start
```

### 3. Executar medições

```bash
python scripts/benchmark.py
```

### 4. Analisar resultados

```bash
python scripts/analyze_results.py
```

## Ambiente Experimental

- **Sistema Operacional**: macOS (darwin 25.1.0)
- **APIs**: Localhost
  - REST: http://localhost:8000
  - GraphQL: http://localhost:8001

## Documentação Adicional

- `experimento_desenho.md` - Desenho completo do experimento
- `ENTREGA.md` - Informações da entrega do Sprint 1
- `QUICKSTART.md` - Guia rápido de execução
- `NOTAS_DESENVOLVIMENTO.md` - Notas sobre decisões de implementação
- `ANTES_DE_ENTREGAR.md` - Checklist antes de entregar

## Referências

- Express.js: https://expressjs.com/
- Apollo Server: https://www.apollographql.com/docs/apollo-server/
- SQLite: https://www.sqlite.org/

