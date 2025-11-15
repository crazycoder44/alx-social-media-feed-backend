# GraphQL API Examples

This document provides example queries and mutations for the Social Media Feed Backend GraphQL API.

## Access GraphQL Playground

- **Local Development**: http://127.0.0.1:8000/graphql/
- **Production**: [Your deployed URL]/graphql/

---

## Queries

### 1. Get All Posts (with Pagination)

```graphql
query {
  allPosts(limit: 10, offset: 0) {
    id
    content
    imageUrl
    createdAt
    updatedAt
    author {
      id
      username
      email
    }
    likesCount
    commentsCount
    sharesCount
  }
}
```

### 2. Get Single Post by ID

```graphql
query {
  post(id: 1) {
    id
    content
    imageUrl
    createdAt
    author {
      id
      username
      firstName
      lastName
    }
    likesCount
    commentsCount
    sharesCount
  }
}
```

### 3. Get Posts by Specific User

```graphql
query {
  userPosts(userId: 1) {
    id
    content
    imageUrl
    createdAt
    likesCount
    commentsCount
    sharesCount
  }
}
```

### 4. Get Comments for a Post

```graphql
query {
  postComments(postId: 1) {
    id
    content
    createdAt
    author {
      id
      username
    }
  }
}
```

### 5. Get Likes for a Post

```graphql
query {
  postLikes(postId: 1) {
    id
    createdAt
    user {
      id
      username
    }
  }
}
```

### 6. Get All Users

```graphql
query {
  allUsers {
    id
    username
    email
    firstName
    lastName
  }
}
```

---

## Mutations

### 1. Create Post

```graphql
mutation {
  createPost(content: "Hello World! This is my first post.", imageUrl: "https://example.com/image.jpg") {
    success
    message
    post {
      id
      content
      imageUrl
      createdAt
      author {
        username
      }
    }
  }
}
```

**Without Image:**
```graphql
mutation {
  createPost(content: "Just a text post without an image.") {
    success
    message
    post {
      id
      content
      createdAt
    }
  }
}
```

### 2. Update Post

```graphql
mutation {
  updatePost(postId: 1, content: "Updated content for this post") {
    success
    message
    post {
      id
      content
      updatedAt
    }
  }
}
```

### 3. Delete Post

```graphql
mutation {
  deletePost(postId: 1) {
    success
    message
  }
}
```

### 4. Add Comment to Post

```graphql
mutation {
  createComment(postId: 1, content: "Great post! Thanks for sharing.") {
    success
    message
    comment {
      id
      content
      createdAt
      author {
        username
      }
    }
  }
}
```

### 5. Delete Comment

```graphql
mutation {
  deleteComment(commentId: 1) {
    success
    message
  }
}
```

### 6. Like/Unlike Post (Toggle)

```graphql
mutation {
  likePost(postId: 1) {
    success
    message
    like {
      id
      createdAt
    }
  }
}
```

**Note:** This mutation toggles the like. If the user hasn't liked the post, it will add a like. If the user has already liked it, it will remove the like.

### 7. Share Post

```graphql
mutation {
  sharePost(postId: 1) {
    success
    message
    share {
      id
      createdAt
      user {
        username
      }
    }
  }
}
```

---

## Combined Query Example

Fetch multiple data types in a single request:

```graphql
query {
  allPosts(limit: 5, offset: 0) {
    id
    content
    author {
      username
    }
    likesCount
    commentsCount
  }
  
  allUsers {
    id
    username
  }
}
```

---

## Error Handling

All mutations return a `success` boolean and a `message` string. Check these fields to handle errors:

```graphql
mutation {
  createPost(content: "Test post") {
    success
    message
    post {
      id
    }
  }
}
```

**Response on Success:**
```json
{
  "data": {
    "createPost": {
      "success": true,
      "message": "Post created successfully",
      "post": {
        "id": "1"
      }
    }
  }
}
```

**Response on Error (Not Authenticated):**
```json
{
  "data": {
    "createPost": {
      "success": false,
      "message": "Authentication required",
      "post": null
    }
  }
}
```

---

## Authentication

⚠️ **Note:** Most mutations require authentication. Make sure you are logged in as a user before attempting to create, update, delete, like, comment, or share posts.

For testing purposes, you can:
1. Create a superuser: `python manage.py createsuperuser`
2. Log in to the Django admin: http://127.0.0.1:8000/admin/
3. Then use the GraphQL Playground in the same browser session

---

## Tips for Using GraphQL Playground

1. **Auto-complete**: Press `Ctrl + Space` to see available fields and arguments
2. **Documentation**: Click "Docs" on the right side to explore the schema
3. **Query Variables**: Use the "Query Variables" panel for dynamic values
4. **Prettify**: Use `Ctrl + Shift + P` to format your query

---

## Next Steps

- Explore the schema using the Docs panel in GraphQL Playground
- Try combining queries and mutations in a single request
- Implement pagination for large datasets
- Add filtering and sorting capabilities
