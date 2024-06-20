# Blog Post Application

This project is a blog post application that allows users to create, view, and delete blog posts. The backend is built with Flask and includes user authentication, while the frontend is currently under development and serves as a basic interface for interacting with the backend API.

## Features

- User Registration and Login
- JWT Authentication
- Create, View, and Delete Blog Posts
- API Endpoints for managing posts

## Project Structure

- `backend_app.py`: The Flask backend application.
- `frontend_app.py`: The Flask application for serving static files.
- `index.html`: The main HTML file for the frontend.
- `styles.css`: CSS file for styling the frontend.
- `main.js`: JavaScript file for frontend logic and API interactions.

## Getting Started

### Prerequisites

- Python 3.7+
- Flask
- Flask-CORS
- Flask-JWT-Extended
- Flask-Limiter
- Werkzeug

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/blog-post-app.git
    cd blog-post-app
    ```

2. Set up a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Create `posts.json` and `users.json` files:
    ```json
    // posts.json
    []

    // users.json
    {}
    ```

### Running the Backend

1. Start the backend server:
    ```bash
    python backend_app.py
    ```
    The backend will run on `http://127.0.0.1:5002`.

### Running the Frontend

1. Start the frontend server:
    ```bash
    python frontend_app.py
    ```
    The frontend will be served on `http://127.0.0.1:5001`.

### API Endpoints

- **User Registration**
    - `POST /api/register`
    - Request Body: `{ "username": "your_username", "password": "your_password" }`

- **User Login**
    - `POST /api/login`
    - Request Body: `{ "username": "your_username", "password": "your_password" }`
    - Response: `{ "access_token": "your_jwt_token" }`

- **Get Posts**
    - `GET /api/posts`

- **Add Post**
    - `POST /api/posts`
    - Request Header: `Authorization: Bearer <your_jwt_token>`
    - Request Body: `{ "title": "Post Title", "content": "Post Content" }`

- **Delete Post**
    - `DELETE /api/posts/<post_id>`
    - Request Header: `Authorization: Bearer <your_jwt_token>`

### Example Usage

1. **Register a User**:
    ```bash
    curl -X POST http://127.0.0.1:5002/api/register -H "Content-Type: application/json" -d '{"username": "testuser", "password": "testpassword"}'
    ```

2. **Login**:
    ```bash
    curl -X POST http://127.0.0.1:5002/api/login -H "Content-Type: application/json" -d '{"username": "testuser", "password": "testpassword"}'
    ```

3. **Get Posts**:
    ```bash
    curl -X GET http://127.0.0.1:5002/api/posts
    ```

4. **Add a Post**:
    ```bash
    curl -X POST http://127.0.0.1:5002/api/posts -H "Authorization: Bearer your_jwt_token" -H "Content-Type: application/json" -d '{"title": "My First Post", "content": "This is the content of my first post."}'
    ```

5. **Delete a Post**:
    ```bash
    curl -X DELETE http://127.0.0.1:5002/api/posts/1 -H "Authorization: Bearer your_jwt_token"
    ```

## To-Do List

- [ ] Complete the frontend with a more user-friendly interface
- [ ] Add more features to the frontend (e.g., update posts, search functionality)
- [ ] Improve error handling and user feedback in the frontend
- [ ] Write unit tests for both backend and frontend

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.

## Contact

For any questions or suggestions, feel free to open an issue or contact me at [your-email@example.com].

---

Thank you for checking out this project! Your feedback and contributions are greatly appreciated.
