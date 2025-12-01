// API GraphQL usando Apollo Server
const express = require('express');
const { ApolloServer } = require('apollo-server-express');
const cors = require('cors');
const typeDefs = require('./schema');
const resolvers = require('./resolvers');

const app = express();
const PORT = 8001;

// Middleware
app.use(cors());

// Desabilitar cache para experimento
app.use((req, res, next) => {
  res.set('Cache-Control', 'no-store, no-cache, must-revalidate, private');
  res.set('Pragma', 'no-cache');
  res.set('Expires', '0');
  next();
});

const server = new ApolloServer({
  typeDefs,
  resolvers,
  // Desabilitar cache no Apollo Server
  cacheControl: {
    defaultMaxAge: 0
  }
});

async function startServer() {
  await server.start();
  server.applyMiddleware({ app, path: '/graphql' });

  // Health check
  app.get('/health', (req, res) => {
    res.json({ status: 'ok', api: 'GraphQL' });
  });

  app.listen(PORT, () => {
    console.log(`API GraphQL rodando em http://localhost:${PORT}${server.graphqlPath}`);
  });
}

startServer().catch(err => {
  console.error('Erro ao iniciar servidor:', err);
});



