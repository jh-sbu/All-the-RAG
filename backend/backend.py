from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from typing import cast

import openai

app = Flask(__name__)

load_dotenv()

# app.secret_key = "change_this_key"  # TODO
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise ValueError("Could not initialize SECRET_KEY for flask")

CORS(app)

api_key = os.environ.get("API_KEY", "fake_key")
base_url = os.environ.get("BASE_URL")
if not base_url:
    raise ValueError("Could not find the url of the LLM server")

model = os.environ.get("MODEL")
if not model:
    raise ValueError("Could not find the name of the model")

client = openai.OpenAI(api_key=api_key, base_url=base_url)

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
    # return jsonify({"error": "Not yet implemented"}), 405
    try:
        global model
        # We already checked this but the lsp needs help realizing it
        model = cast(str, model)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "assistant",
                    "content": "You are a helpful assistant. Respond to the user's query.",
                }
            ],
            model=model,
            max_completion_tokens=32,
        )

        return jsonify({"response": chat_completion.choices[0].message.content})
    except:
        return jsonify({"error": "Error reaching chatbot"}), 500
    return jsonify({"response": "Chat bot is not currently running"}), 200


@app.route("/example_page", methods=["GET"])
def get_example():
    return jsonify({"key": "value"}), 200


if __name__ == "__main__":
    app.run(debug=True)
