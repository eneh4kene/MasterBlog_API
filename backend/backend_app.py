from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


# validate user data
def invalid_data(new_post):
    if 'title' not in new_post:
        return jsonify({"error": "post's title is missing"}), 400
    elif 'content' not in new_post:
        return jsonify({"error": "post's content is missing"}), 400
    return None


@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    # handle post requests
    if request.method == 'POST':
        new_post = request.get_json()

        # check if post is valid
        error_response = invalid_data(new_post)
        if error_response:
            return error_response[0], error_response[1]
        new_post_id = max(post['id'] for post in POSTS) + 1
        new_post['id'] = new_post_id
        POSTS.append(new_post)
        return jsonify(POSTS), 201
    return jsonify(POSTS)


def find_post_by_id(post_id):
    return next((post for post in POSTS if post['id'] == post_id), None)


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    # find the post with the given id.
    post = find_post_by_id(id)

    if post is None:
        error_message = {"message": "Post with the id not found."}
        return jsonify(error_message), 404

    POSTS.remove(post)

    return jsonify({"message": f"Post with id '{id}' has been deleted successfully."}), 200


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    # Find the post with the given ID
    post = find_post_by_id(id)

    # If the post wasn't found, return a 404 error
    if post is None:
        return f'Sorry, no book with book ID: {id}', 404

    # Update the post with the new data
    new_data = request.get_json()

    # update the post
    post.update(new_data)

    # Return the updated post
    return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_query = request.args.get('title', default='', type=str)
    content_query = request.args.get('content', default='', type=str)

    filtered_posts = [
        post for post in POSTS
        if (title_query.lower() in post['title'].lower() or content_query.lower() in post['content'].lower())
    ]

    if filtered_posts:
        return jsonify(filtered_posts)
    else:
        return jsonify([])


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
