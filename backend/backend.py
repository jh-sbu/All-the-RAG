from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
from vdb.faiss import FaissIndex
from providers.openrouter import OpenRouter
from providers.llama_server import Llama
import logging

app = Flask(__name__)

load_dotenv()

log_level = os.environ.get("LOG_LEVEL")
if not log_level:
    log_level = logging.INFO
else:
    if log_level == "debug":
        log_level = logging.DEBUG
    elif log_level == "info":
        log_level = logging.INFO
    elif log_level == "warn":
        log_level = logging.WARNING
    elif log_level == "error":
        log_level = logging.ERROR
    elif log_level == "critical":
        log_level = logging.CRITICAL
    else:
        log_level = logging.INFO

logging.basicConfig(
    level=log_level, format="[%(asctime)s] [%(levelname)-8s] [%(name)s]: %(message)s"
)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise ValueError("Could not initialize SECRET_KEY for flask")

CORS(app)

example_faiss = FaissIndex("sandbox/example_faiss.faiss")
example_faiss.get_nearest(3, "What is a woodchuck in minecraft?")

# print(example_faiss.index)

# example_faiss.save_faiss("sandbox/example_faiss.faiss")

# faiss.write_index(example_faiss.model, "example_index.faiss")

system_prompt = "You are a helpful assistant that assists users with the All the Mods modpacks for the video game Minecraft. Read the provided context and use it to respond to the user's query. Be concise - your job is to find the relevant information in the given context, not repeat everything you see word for word."

completion_provider = os.environ.get("COMPLETION_PROVIDER")
if completion_provider is None:
    raise ValueError("Could not find completion provider configuration")
elif completion_provider == "Local":
    provider = Llama(system_prompt=system_prompt)
elif completion_provider == "OpenRouter":
    provider = OpenRouter(system_prompt=system_prompt)
else:
    raise ValueError("Specified completion provider is not supported")


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
    data = request.get_json()

    if data is None or "messages" not in data.keys():
        return jsonify({"error": "No user prompt received"}), 400

    else:
        try:
            # TODO fix this kludge - why is the model failing to encode if
            # I don't do this?
            full_message = " ".join(
                [message["content"] for message in data["messages"]]
            )
            contexts = example_faiss.get_nearest(3, full_message)
            return provider.request(contexts, data["messages"])

        except Exception as e:
            app.logger.error(f"Error in chat stream: {str(e)}")
            return jsonify({"error": "Error reaching chatbot"}), 500


@app.route("/example_page", methods=["GET"])
def get_example():
    return jsonify({"key": "value"}), 200


if __name__ == "__main__":
    app.run(debug=True)
