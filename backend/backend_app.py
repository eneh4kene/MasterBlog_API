import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this to a secure key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # Set token expiration to 1 hour

jwt = JWTManager(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

USERS_DB = 'users.json'
POSTS_FILE = 'posts.json'

# Load users from JSON file, handle empty or invalid files
if os.path.exists(USERS_DB):
    try:
        with open(USERS_DB, 'r') as user_obj:
            USERS = json.load(user_obj)
    except (json.JSONDecodeError, FileNotFoundError):
        USERS = {}
else:
    USERS = {}

# Load posts from JSON file, handle empty or invalid files
if os.path.exists(POSTS_FILE):
    try:
        with open(POSTS_FILE, 'r') as file_obj:
            POSTS = json.load(file_obj)
    except (json.JSONDecodeError, FileNotFoundError):
        POSTS = []
else:
    POSTS = []


# Save users to JSON file
def save_users():
    with open(USERS_DB, 'w') as user_ob:
        json.dump(USERS, user_ob, indent=4)


# Save posts to JSON file
def save_posts():
    with open(POSTS_FILE, 'w') as file_ob:
        json.dump(POSTS, file_ob, indent=4)


# User registration endpoint
@app.route('/api/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"error": "Username and password must be strings"}), 400

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if username in USERS:
        return jsonify({"error": "User already exists"}), 400

    USERS[username] = generate_password_hash(password)
    save_users()
    return jsonify({"message": "User registered successfully"}), 201


# User login endpoint
@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"error": "Username and password must be strings"}), 400

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user_password_hash = USERS.get(username)
    if not user_password_hash or not check_password_hash(user_password_hash, password):
        return jsonify({"error": "Invalid username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


# Validate post data
def validate_data(new_post):
    required_fields = ['title', 'content', 'author', 'date']
    for field in required_fields:
        if field not in new_post:
            return {"error": f"post's {field} is missing"}, 400
    try:
        datetime.strptime(new_post['date'], '%Y-%m-%d')
    except ValueError:
        return {"error": "date format should be YYYY-MM-DD"}, 400
    return None


@app.route('/api/posts', methods=['GET', 'POST'])
@limiter.limit("100 per hour")
@jwt_required(optional=True)
def handle_posts():
    if request.method == 'POST':
        current_user = get_jwt_identity()
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        new_post = request.get_json()
        error_response = validate_data(new_post)
        if error_response:
            return jsonify(error_response), 400

        new_post_id = max(post['id'] for post in POSTS) + 1 if POSTS else 1
        new_post['id'] = new_post_id
        new_post['user_id'] = current_user
        POSTS.append(new_post)
        save_posts()
        return jsonify(new_post), 201

    # Handle GET request with pagination and sorting
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_field = request.args.get('sort')
    sort_direction = request.args.get('direction', 'asc')

    valid_sort_fields = ['title', 'content', 'author', 'date']
    if sort_field and sort_field not in valid_sort_fields:
        return jsonify({"error": f"Invalid sort field: {sort_field}"}), 400
    if sort_direction not in ['asc', 'desc']:
        return jsonify({"error": f"Invalid sort direction: {sort_direction}"}), 400

    sorted_posts = POSTS
    if sort_field:
        reverse = (sort_direction == 'desc')
        if sort_field == 'date':
            sorted_posts = sorted(POSTS, key=lambda x: datetime.strptime(x[sort_field], '%Y-%m-%d'), reverse=reverse)
        else:
            sorted_posts = sorted(POSTS, key=lambda x: x[sort_field], reverse=reverse)

    start = (page - 1) * per_page
    end = start + per_page
    paginated_posts = sorted_posts[start:end]

    response = {
        "page": page,
        "per_page": per_page,
        "total_posts": len(POSTS),
        "posts": paginated_posts
    }
    return jsonify(response)


def find_post_by_id(post_id):
    return next((post for post in POSTS if post['id'] == post_id), None)


@app.route('/api/posts/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_post(id):
    current_user = get_jwt_identity()
    post = find_post_by_id(id)

    if post is None:
        return jsonify({"message": "Post with the id not found."}), 404

    if post['user_id'] != current_user:
        return jsonify({"error": "Unauthorized"}), 403

    POSTS.remove(post)
    save_posts()
    return jsonify({"message": f"Post with id '{id}' has been deleted successfully."}), 200


@app.route('/api/posts/<int:id>', methods=['PUT'])
@jwt_required()
def update_post(id):
    current_user = get_jwt_identity()
    post = find_post_by_id(id)

    if post is None:
        return jsonify({"message": f"Sorry, no post with ID: {id}"}), 404

    if post['user_id'] != current_user:
        return jsonify({"error": "Unauthorized"}), 403

    new_data = request.get_json()
    error_response = validate_data(new_data)
    if error_response:
        return jsonify(error_response), 400

    post.update(new_data)
    save_posts()
    return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
@limiter.limit("100 per hour")
def search_posts():
    title_query = request.args.get('title', default='', type=str)
    content_query = request.args.get('content', default='', type=str)
    author_query = request.args.get('author', default='', type=str)
    date_query = request.args.get('date', default='', type=str)

    filtered_posts = [
        post for post in POSTS
        if (title_query.lower() in post['title'].lower() or
            content_query.lower() in post['content'].lower() or
            author_query.lower() in post['author'].lower() or
            date_query in post['date'])
    ]

    return jsonify(filtered_posts)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
