// Resolvers GraphQL
const { getDatabase } = require('../shared/database');
const { User, Post, Comment, Category } = require('../shared/models');

const db = getDatabase();

// Helper para promisificar queries do SQLite
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

const resolvers = {
  Query: {
    // Cenário 1: Consulta Simples
    user: async (parent, args) => {
      const row = await dbGet('SELECT * FROM users WHERE id = ?', [args.id]);
      return row ? new User(row) : null;
    },

    // Cenário 2: Lista Simples
    users: async () => {
      const rows = await dbQuery('SELECT * FROM users');
      return rows.map(row => new User(row));
    },

    // Cenário 3: Lista com Filtros
    usersFiltered: async (parent, args) => {
      let sql = 'SELECT * FROM users WHERE 1=1';
      const params = [];
      
      if (args.status) {
        sql += ' AND status = ?';
        params.push(args.status);
      }
      
      const limit = args.limit || 10;
      sql += ' LIMIT ?';
      params.push(limit);
      
      const rows = await dbQuery(sql, params);
      return rows.map(row => new User(row));
    },

    // Cenário 6: Múltiplos Recursos
    multiple: async () => {
      const [users, posts, comments] = await Promise.all([
        dbQuery('SELECT * FROM users'),
        dbQuery('SELECT * FROM posts'),
        dbQuery('SELECT * FROM comments')
      ]);
      
      return {
        users: users.map(row => new User(row)),
        posts: posts.map(row => new Post(row)),
        comments: comments.map(row => new Comment(row))
      };
    }
  },

  User: {
    // Cenário 4: Recursos Relacionados
    posts: async (parent) => {
      const rows = await dbQuery(
        'SELECT * FROM posts WHERE user_id = ?',
        [parent.id]
      );
      return rows.map(row => new Post(row));
    }
  },

  Post: {
    user: async (parent) => {
      const row = await dbGet('SELECT * FROM users WHERE id = ?', [parent.userId]);
      return row ? new User(row) : null;
    },
    comments: async (parent) => {
      const rows = await dbQuery(
        'SELECT * FROM comments WHERE post_id = ?',
        [parent.id]
      );
      return rows.map(row => new Comment(row));
    }
  }
};

module.exports = resolvers;




