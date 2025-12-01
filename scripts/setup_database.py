#!/usr/bin/env python3
"""
Script para criar o banco de dados SQLite e popular com dados sintéticos.
Usa Faker para gerar dados realistas.
"""

import sqlite3
import os
import random
from faker import Faker
from datetime import datetime, timedelta

# Configuração do caminho do banco
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DB_DIR, 'experiment.db')

# Quantidades para dataset - valores escolhidos para ter volume suficiente
NUM_USERS = 1000
NUM_POSTS = 5000
NUM_COMMENTS = 15000
NUM_CATEGORIES = 50

# Faker com locale brasileiro para dados mais realistas
fake = Faker(['pt_BR'])

def create_database():
    """Cria o banco de dados e as tabelas."""
    # Criar diretório se não existir
    os.makedirs(DB_DIR, exist_ok=True)
    
    # Remover banco existente
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Banco de dados existente removido: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Criar tabelas
    print("Criando tabelas...")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            category_id INTEGER,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (post_id) REFERENCES posts(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Criar índices para performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_status ON users(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id)')
    
    conn.commit()
    print("Tabelas criadas com sucesso!")
    
    return conn, cursor

def populate_categories(cursor):
    """Popula a tabela de categorias."""
    print(f"Populando {NUM_CATEGORIES} categorias...")
    
    categories = []
    for _ in range(NUM_CATEGORIES):
        categories.append((
            fake.word().capitalize(),
            fake.sentence()
        ))
    
    cursor.executemany(
        'INSERT INTO categories (name, description) VALUES (?, ?)',
        categories
    )
    
    print("Categorias populadas!")

def populate_users(cursor):
    """Popula a tabela de usuários."""
    print(f"Populando {NUM_USERS} usuários...")
    
    users = []
    statuses = ['active', 'inactive', 'pending']
    
    for _ in range(NUM_USERS):
        created_at = fake.date_time_between(
            start_date='-2y',
            end_date='now'
        ).isoformat()
        
        users.append((
            fake.name(),
            fake.email(),
            random.choice(statuses),
            created_at
        ))
    
    cursor.executemany(
        'INSERT INTO users (name, email, status, created_at) VALUES (?, ?, ?, ?)',
        users
    )
    
    print("Usuários populados!")
    
    return cursor.lastrowid

def populate_posts(cursor, num_users, num_categories):
    """Popula a tabela de posts."""
    print(f"Populando {NUM_POSTS} posts...")
    
    posts = []
    
    for _ in range(NUM_POSTS):
        user_id = random.randint(1, num_users)
        category_id = random.randint(1, num_categories) if random.random() > 0.1 else None
        
        created_at = fake.date_time_between(
            start_date='-1y',
            end_date='now'
        ).isoformat()
        
        posts.append((
            fake.sentence(nb_words=6),
            fake.text(max_nb_chars=500),
            user_id,
            category_id,
            created_at
        ))
    
    cursor.executemany(
        'INSERT INTO posts (title, content, user_id, category_id, created_at) VALUES (?, ?, ?, ?, ?)',
        posts
    )
    
    print("Posts populados!")
    
    return cursor.lastrowid

def populate_comments(cursor, num_users, num_posts):
    """Popula a tabela de comentários."""
    print(f"Populando {NUM_COMMENTS} comentários...")
    
    comments = []
    
    for _ in range(NUM_COMMENTS):
        post_id = random.randint(1, num_posts)
        user_id = random.randint(1, num_users)
        
        created_at = fake.date_time_between(
            start_date='-6m',
            end_date='now'
        ).isoformat()
        
        comments.append((
            fake.text(max_nb_chars=200),
            post_id,
            user_id,
            created_at
        ))
    
    cursor.executemany(
        'INSERT INTO comments (text, post_id, user_id, created_at) VALUES (?, ?, ?, ?)',
        comments
    )
    
    print("Comentários populados!")

def main():
    """Função principal."""
    print("=" * 50)
    print("Setup do Banco de Dados - Experimento GraphQL vs REST")
    print("=" * 50)
    
    conn, cursor = create_database()
    
    try:
        populate_categories(cursor)
        num_categories = NUM_CATEGORIES
        
        populate_users(cursor)
        num_users = NUM_USERS
        
        populate_posts(cursor, num_users, num_categories)
        num_posts = NUM_POSTS
        
        populate_comments(cursor, num_users, num_posts)
        
        conn.commit()
        
        # Estatísticas
        cursor.execute('SELECT COUNT(*) FROM users')
        users_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM posts')
        posts_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM comments')
        comments_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM categories')
        categories_count = cursor.fetchone()[0]
        
        print("\n" + "=" * 50)
        print("Banco de dados criado com sucesso!")
        print("=" * 50)
        print(f"Localização: {DB_PATH}")
        print(f"Usuários: {users_count}")
        print(f"Posts: {posts_count}")
        print(f"Comentários: {comments_count}")
        print(f"Categorias: {categories_count}")
        print("=" * 50)
        
    except Exception as e:
        conn.rollback()
        print(f"\nErro ao popular banco de dados: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    main()

