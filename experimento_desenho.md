# Desenho do Experimento: GraphQL vs REST

## Perguntas de Pesquisa

- **RQ1**: Respostas às consultas GraphQL são mais rápidas que respostas às consultas REST?
- **RQ2**: Respostas às consultas GraphQL têm tamanho menor que respostas às consultas REST?

---

## A. Hipóteses Nula e Alternativa

### RQ1 - Tempo de Resposta

- **H₀₁**: Não há diferença estatisticamente significativa no tempo de resposta entre consultas GraphQL e REST.
- **Hₐ₁**: Consultas GraphQL apresentam tempo de resposta estatisticamente menor que consultas REST.

### RQ2 - Tamanho da Resposta

- **H₀₂**: Não há diferença estatisticamente significativa no tamanho da resposta entre consultas GraphQL e REST.
- **Hₐ₂**: Consultas GraphQL apresentam tamanho de resposta estatisticamente menor que consultas REST.

---

## B. Variáveis Dependentes

1. **Tempo de Resposta (ms)**: Tempo decorrido desde o envio da requisição até o recebimento completo da resposta.
2. **Tamanho da Resposta (bytes)**: Tamanho total em bytes do corpo da resposta HTTP recebida.

---

## C. Variáveis Independentes

1. **Tipo de API**: GraphQL ou REST (fator principal do experimento)
2. **Tipo de Consulta**: Diferentes cenários de consulta (simples, com múltiplos recursos, com filtros, com relações)
3. **Volume de Dados**: Número de registros retornados na resposta
4. **Complexidade da Consulta**: Número de campos/atributos solicitados

---

## D. Tratamentos

O experimento terá **dois tratamentos principais**:

1. **T1 - API REST**: Consultas realizadas através de endpoints REST tradicionais
2. **T2 - API GraphQL**: Consultas realizadas através de queries GraphQL

### Cenários de Teste (Objetos Experimentais)

Cada tratamento será aplicado aos seguintes cenários:

1. **Cenário 1 - Consulta Simples**: Buscar um único recurso com todos os campos
   - REST: `GET /api/users/1`
   - GraphQL: `query { user(id: 1) { id, name, email } }`

2. **Cenário 2 - Lista Simples**: Buscar lista de recursos sem filtros
   - REST: `GET /api/users`
   - GraphQL: `query { users { id, name, email } }`

3. **Cenário 3 - Lista com Filtros**: Buscar lista de recursos com filtros
   - REST: `GET /api/users?status=active&limit=10`
   - GraphQL: `query { users(status: "active", limit: 10) { id, name, email } }`

4. **Cenário 4 - Recursos Relacionados**: Buscar recurso com dados relacionados
   - REST: `GET /api/users/1/posts` (requisição adicional)
   - GraphQL: `query { user(id: 1) { id, name, posts { id, title } } }`

5. **Cenário 5 - Consulta Seletiva**: Buscar apenas campos específicos
   - REST: `GET /api/users/1` (retorna todos os campos)
   - GraphQL: `query { user(id: 1) { id, name } }`

6. **Cenário 6 - Consulta com Múltiplos Recursos**: Buscar diferentes tipos de recursos
   - REST: Múltiplas requisições `GET /api/users`, `GET /api/posts`, `GET /api/comments`
   - GraphQL: `query { users { id, name }, posts { id, title }, comments { id, text } }`

---

## E. Objetos Experimentais

Os objetos experimentais serão **consultas HTTP** realizadas contra as APIs. Cada objeto experimental consiste em:

- Uma requisição HTTP (REST ou GraphQL)
- A medição do tempo de resposta
- A medição do tamanho da resposta

As consultas serão realizadas sobre um **dataset sintético** de:
- Usuários (users)
- Posts (posts)
- Comentários (comments)
- Categorias (categories)

---

## F. Tipo de Projeto Experimental

**Experimento Controlado (Controlled Experiment)** dentro do sujeito (within-subjects) com **replicação completa**.

- Cada consulta será executada múltiplas vezes (replicações)
- As mesmas consultas lógicas serão testadas em ambas as APIs
- Ambiente controlado com condições fixas (mesma máquina, mesma rede, mesmo dataset)

**Design**: Fatorial completo 2x6
- 2 tipos de API (REST, GraphQL)
- 6 cenários de teste
- Total de 12 combinações de tratamento-cenário

---

## G. Quantidade de Medições

### Replicações por Cenário

- **30 replicações** por combinação de tratamento-cenário
- **Total de execuções**: 2 tratamentos × 6 cenários × 30 replicações = **360 execuções**

### Justificativa

- 30 replicações permitem aplicar testes estatísticos robustos (ex: teste t de Student, Mann-Whitney)
- Permite análise de distribuição, outliers e variabilidade
- Aproximadamente 5% de nível de significância com poder estatístico adequado

### Randomização

- Ordem de execução dos tratamentos será randomizada
- Ordem dos cenários será randomizada dentro de cada tratamento
- Intervalo de 1 segundo entre execuções para evitar efeitos de cache/overhead

---

## H. Ameaças à Validade

### Ameaças à Validade Interna

1. **Efeitos de Cache**: Respostas podem ser cacheadas pelo servidor ou cliente
   - *Mitigação*: Desabilitar cache HTTP, limpar cache entre execuções, adicionar timestamps nas requisições

2. **Condições de Rede**: Variações na latência de rede podem afetar resultados
   - *Mitigação*: Executar localmente (localhost), medir tempo no cliente (não incluir latência de rede)

3. **Carga do Sistema**: Outros processos podem afetar performance
   - *Mitigação*: Executar em ambiente isolado, monitorar uso de CPU/memória, realizar múltiplas medições

4. **Ordem de Execução**: Efeitos de aprendizado ou aquecimento
   - *Mitigação*: Randomizar ordem de execução, incluir período de warm-up

5. **Implementação das APIs**: Diferenças na qualidade da implementação podem afetar comparação
   - *Mitigação*: Usar bibliotecas populares e bem mantidas, seguir boas práticas em ambas implementações

### Ameaças à Validade Externa

1. **Dataset Sintético**: Resultados podem não refletir dados reais
   - *Mitigação*: Usar dataset representativo com tamanhos variados e relações complexas

2. **Escopo Limitado**: Apenas alguns cenários de uso são testados
   - *Mitigação*: Incluir cenários variados (simples, complexos, com relações)

3. **Ambiente Local**: Resultados podem diferir em produção
   - *Mitigação*: Documentar ambiente completo, realizar experimento em condições controladas e reproduzíveis

4. **Tamanho do Dataset**: Dataset pode não representar volumes reais
   - *Mitigação*: Incluir diferentes volumes de dados nos testes

### Ameaças à Validade de Construção

1. **Definição de "Performance"**: Tempo de resposta pode incluir overheads não relacionados à API
   - *Mitigação*: Medir apenas o tempo de processamento da resposta, excluir parsing/serialização se aplicável

2. **Definição de "Tamanho"**: Tamanho pode variar dependendo da codificação
   - *Mitigação*: Medir tamanho em bytes do corpo da resposta HTTP bruta

---

## I. Ambiente Experimental

### Hardware
- Sistema operacional: macOS (darwin 25.1.0)
- Processador: [A definir durante execução]
- Memória: [A definir durante execução]

### Software
- Python 3.x (para scripts de medição)
- Node.js (para implementação das APIs)
- Bibliotecas:
  - FastAPI ou Express.js (REST)
  - Apollo Server ou GraphQL Yoga (GraphQL)
  - Requests/HTTPX (cliente HTTP para medições)
  - Pandas (análise de dados)
  - NumPy/Scipy (análise estatística)

### Dataset
- Base de dados sintética com:
  - 1000 usuários
  - 5000 posts
  - 15000 comentários
  - 50 categorias

### Execução
- APIs rodando em localhost
- Porta 8000 (REST) e 8001 (GraphQL)
- Sem cache habilitado
- Ambiente isolado (sem outras aplicações rodando)

---

## J. Plano de Execução

1. **Setup do Ambiente**
   - Instalar dependências
   - Criar dataset sintético
   - Implementar APIs REST e GraphQL

2. **Scripts de Medição**
   - Desenvolver script para realizar requisições
   - Implementar coleta de métricas (tempo, tamanho)
   - Salvar resultados em CSV/JSON

3. **Execução dos Trials**
   - Executar warm-up (10 requisições descartadas)
   - Executar 30 replicações por combinação
   - Randomizar ordem de execução
   - Registrar todas as métricas

4. **Validação dos Dados**
   - Verificar outliers
   - Validar completude dos dados
   - Verificar consistência

5. **Análise Estatística**
   - Estatísticas descritivas (média, mediana, desvio padrão)
   - Testes de normalidade (Shapiro-Wilk)
   - Testes de hipóteses (teste t ou Mann-Whitney)
   - Intervalos de confiança



