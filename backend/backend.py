from flask import Flask, jsonify

app = Flask(__name__)
app.secret_key = "change_this_key"  # TODO

not_implemented_error = jsonify({"error": "Not yet implemented"}), 501


@app.route("/register", methods=["POST"])
def register():
    return not_implemented_error


@app.route("/login", methods=["POST"])
def login():
    return not_implemented_error


@app.route("/chat_history", methods=["GET"])
def get_chat_history():
    return not_implemented_error


@app.route("/send_messages", methods=["POST"])
def send_message():
    return not_implemented_error
