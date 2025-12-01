// Schema GraphQL
const { gql } = require('apollo-server-express');

const typeDefs = gql`
  type User {
    id: ID!
    name: String!
    email: String!
    status: String!
    createdAt: String!
    posts: [Post!]
  }

  type Post {
    id: ID!
    title: String!
    content: String!
    userId: ID!
    categoryId: ID
    createdAt: String!
    user: User
    comments: [Comment!]
  }

  type Comment {
    id: ID!
    text: String!
    postId: ID!
    userId: ID!
    createdAt: String!
  }

  type Category {
    id: ID!
    name: String!
    description: String
  }

  type Query {
    # Cenário 1: Consulta Simples
    user(id: ID!): User
    
    # Cenário 2: Lista Simples
    users: [User!]!
    
    # Cenário 3: Lista com Filtros
    usersFiltered(status: String, limit: Int): [User!]!
    
    # Cenário 5: Consulta Seletiva (incluído no user query através de seleção de campos)
    
    # Cenário 6: Múltiplos Recursos
    multiple: MultipleResources!
  }

  type MultipleResources {
    users: [User!]!
    posts: [Post!]!
    comments: [Comment!]!
  }
`;

module.exports = typeDefs;

