// API REST usando Express
const express = require('express');
const cors = require('cors');
const { getDatabase } = require('../shared/database');
const { User, Post, Comment, Category } = require('../shared/models');

const app = express();
const PORT = 8000;

// Middleware básico
app.use(cors());
app.use(express.json());

// Desabilitar cache - importante para o experimento não ter viés
app.use((req, res, next) => {
  res.set('Cache-Control', 'no-store, no-cache, must-revalidate, private');
  res.set('Pragma', 'no-cache');
  res.set('Expires', '0');
  next();
});

const db = getDatabase();

// Helper para usar SQLite com async/await (sqlite3 usa callbacks)
function dbQuery(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

function dbGet(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
}

// CENÁRIO 1: Consulta Simples - buscar um usuário por ID
app.get('/api/users/:id', async (req, res) => {
  try {
    const userId = parseInt(req.params.id);
    const row = await dbGet('SELECT * FROM users WHERE id = ?', [userId]);
    
    if (!row) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    const user = new User(row);
    res.json(user.toJSON());
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// CENÁRIO 2: Lista Simples - buscar todos os usuários
app.get('/api/users', async (req, res) => {
  try {
    const rows = await dbQuery('SELECT * FROM users');
    const users = rows.map(row => new User(row).toJSON());
    res.json(users);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// CENÁRIO 3: Lista com Filtros - filtrar por status e limitar quantidade
app.get('/api/users-filtered', async (req, res) => {
  try {
    const status = req.query.status || null;
    const limit = parseInt(req.query.limit) || 10;
    
    let sql = 'SELECT * FROM users WHERE 1=1';
    const params = [];
    
    if (status) {
      sql += ' AND status = ?';
      params.push(status);
    }
    
    sql += ' LIMIT ?';
    params.push(limit);
    
    const rows = await dbQuery(sql, params);
    const users = rows.map(row => new User(row).toJSON());
    res.json(users);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============ CENÁRIO 4: Recursos Relacionados ============
// GET /api/users/:id/posts
app.get('/api/users/:id/posts', async (req, res) => {
  try {
    const userId = parseInt(req.params.id);
    const rows = await dbQuery(
      'SELECT * FROM posts WHERE user_id = ?',
      [userId]
    );
    const posts = rows.map(row => new Post(row).toJSON());
    res.json(posts);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============ CENÁRIO 5: Consulta Seletiva (todos os campos retornados) ============
// GET /api/users/:id/simple - retorna apenas id e name
app.get('/api/users/:id/simple', async (req, res) => {
  try {
    const userId = parseInt(req.params.id);
    const row = await dbGet('SELECT id, name FROM users WHERE id = ?', [userId]);
    
    if (!row) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    res.json({ id: row.id, name: row.name });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ============ CENÁRIO 6: Múltiplos Recursos ============
// GET /api/multiple
app.get('/api/multiple', async (req, res) => {
  try {
    const [users, posts, comments] = await Promise.all([
      dbQuery('SELECT * FROM users'),
      dbQuery('SELECT * FROM posts'),
      dbQuery('SELECT * FROM comments')
    ]);
    
    res.json({
      users: users.map(row => new User(row).toJSON()),
      posts: posts.map(row => new Post(row).toJSON()),
      comments: comments.map(row => new Comment(row).toJSON())
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', api: 'REST' });
});

app.listen(PORT, () => {
  console.log(`API REST rodando em http://localhost:${PORT}`);
});

