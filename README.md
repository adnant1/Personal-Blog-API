# Personal Blog API

This is a RESTful API built using Flask, Python, and MySQL that allows users to create and manage blog posts. It features user authentication using JWT tokens and provides basic CRUD operations for managing blogs and users. The API also includes search functionality, allowing users to find their own blogs as well as the blogs of other users.

## Features

- **User Authentication**: Secure user authentication using JWT tokens.
- **Blog Management**: Create, read, update, and delete blog posts.
- **User Management**: Register new users, view user details.
- **Search**: Filter blogs by author.
- **JWT-based Authentication**: Routes are protected, allowing only authenticated users to perform actions.

## Technologies Used

- **Flask**: Web framework for Python
- **MySQL**: Relational database for storing user and blog information
- **JWT**: Token-based authentication for securing routes
- **Python**: Backend programming language

## Endpoints

### Admin User Endpoints

| Method  | Endpoint             | Description                                     |
|---------|----------------------|-------------------------------------------------|
| `GET`   | `/users`             | Get a list of all the users.                    |
| `GET`   | `/user/<public_id>`  | Get a specific user by `public_id`              |
| `DELETE`| `/user/<public_id>`  | Delete a specific user by `public_id`           |
| `POST`  | `/user/<public_id>`  | Promote a specific user to admin by `public_id` |
| `GET`   | `/blogs`             | Return a list of all blogs in the database      |

### User Endpoints

| Method | Endpoint             | Description                                 |
|--------|----------------------|---------------------------------------------|
| `POST` | `/users/signup`      | Register a new user                         |
| `POST` | `/users/login`       | Login and receive a JWT token               |

### Blog Endpoints

| Method  | Endpoint                 | Description (Authentication Required)       |
|---------|--------------------------|---------------------------------------------|
| `POST`  | `/blog`                  | Create a new blog post                      |
| `GET`   | `/blogs/<author_name>`   | Get all blogs by a specific user            |
| `PUT`   | `/blogs/<blog_id>`       | User can update their own blog              |
| `DELETE`| `/blogs/<blog_id>`       | User can delete their own blog              |

## Authentication

The API uses **JWT (JSON Web Token)** for authentication. To access certain routes (e.g., creating, updating, or deleting blogs), you must include a valid token in the `x-access-token` header of the request.

- **Register**: Users can sign up with a username and password.
- **Login**: Users can log in with their username and password to receive a JWT token.
