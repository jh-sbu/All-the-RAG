from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)

# app.secret_key = "change_this_key"  # TODO
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise ValueError("Could not initialize SECRET_KEY for flask")

CORS(app)

# not_implemented_error = jsonify({"error": "Not yet implemented"}), 501


@app.route("/register", methods=["POST"])
def register():
    # return not_implemented_error
    return jsonify({"error": "Not yet implemented"}), 405


@app.route("/login", methods=["POST"])
def login():
    # return not_implemented_error
    return jsonify({"error": "Not yet implemented"}), 405


@app.route("/past_chats", methods=["GET"])
def get_histories():
    # return not_implemented_error
    return jsonify({"error": "Not implemented yet"})


@app.route("/chat_history", methods=["GET"])
def get_chat_history():
    # return not_implemented_error
    return jsonify({"error": "Not yet implemented"}), 405


@app.route("/send_message", methods=["POST"])
def send_message():
    # return not_implemented_error
    return jsonify({"error": "Not yet implemented"}), 405
    # return jsonify({"response": "Chat bot is not currently running"}), 200


@app.route("/example_page", methods=["GET"])
def get_example():
    return jsonify({"key": "value"}), 200


if __name__ == "__main__":
    app.run(debug=True)
