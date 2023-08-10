from flask import Flask, request, jsonify
from flask_cors import CORS
from recommendations import get_recommendations

app = Flask(__name__)
# CORS(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route('/', methods=['GET'])
def home():
    return "Welcome to the recommendation service!"


@app.route('/recommendations', methods=['GET'])
def recommendations():
    user_id = request.args.get('user_id', type=int)
    recommended_professionals = get_recommendations(user_id)
    return jsonify(recommended_professionals.tolist())


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response


if __name__ == '__main__':
    app.run(debug=True)
