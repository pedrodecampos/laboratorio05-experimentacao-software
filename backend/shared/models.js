// Modelos de dados compartilhados

class User {
  constructor(row) {
    this.id = row.id;
    this.name = row.name;
    this.email = row.email;
    this.status = row.status;
    this.createdAt = row.created_at;
  }

  toJSON() {
    return {
      id: this.id,
      name: this.name,
      email: this.email,
      status: this.status,
      createdAt: this.createdAt
    };
  }
}

class Post {
  constructor(row) {
    this.id = row.id;
    this.title = row.title;
    this.content = row.content;
    this.userId = row.user_id;
    this.categoryId = row.category_id;
    this.createdAt = row.created_at;
  }

  toJSON() {
    return {
      id: this.id,
      title: this.title,
      content: this.content,
      userId: this.userId,
      categoryId: this.categoryId,
      createdAt: this.createdAt
    };
  }
}

class Comment {
  constructor(row) {
    this.id = row.id;
    this.text = row.text;
    this.postId = row.post_id;
    this.userId = row.user_id;
    this.createdAt = row.created_at;
  }

  toJSON() {
    return {
      id: this.id,
      text: this.text,
      postId: this.postId,
      userId: this.userId,
      createdAt: this.createdAt
    };
  }
}

class Category {
  constructor(row) {
    this.id = row.id;
    this.name = row.name;
    this.description = row.description;
  }

  toJSON() {
    return {
      id: this.id,
      name: this.name,
      description: this.description
    };
  }
}

module.exports = {
  User,
  Post,
  Comment,
  Category
};



