from flask import Flask, Response, jsonify, request, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv
import os

from vdb.amazons3vector import AmazonS3Vector
from vdb.faiss import FaissIndex
from providers.openrouter import OpenRouter
from providers.llama_server import Llama
import logging


backend = Flask(__name__)

load_dotenv()

log_level = os.environ.get("LOG_LEVEL")
print(f"Log level: {log_level}")
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


logger = logging.getLogger(__name__)
logger.setLevel(log_level)

backend.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
if not backend.config["SECRET_KEY"]:
    raise ValueError("Could not initialize SECRET_KEY for flask")

CORS(backend)

vdb_provider = os.environ.get("VDB")


vector_db = (
    FaissIndex()
    if vdb_provider == "FAISS"
    else AmazonS3Vector(log_level=log_level)
    if vdb_provider == "Amazon S3 Vector"
    # Default fallback
    else FaissIndex()
)

logger.debug(f"VDB provider read as: {vdb_provider}")
logger.debug(f"Created vector db interface of type {type(vector_db)}")

system_prompt = "You are a helpful assistant that assists users with the All the Mods modpacks for the video game Minecraft. Read the provided context and use it to respond to the user's query. Be concise - your job is to find the relevant information in the given context, not repeat everything you see word for word."

completion_provider = os.environ.get("COMPLETION_PROVIDER")
if completion_provider is None:
    raise ValueError("Could not find completion provider configuration")
elif completion_provider == "Local":
    provider = Llama(system_prompt=system_prompt)
elif completion_provider == "OpenRouter":
    provider = OpenRouter(system_prompt=system_prompt, log_level=log_level)
else:
    raise ValueError("Specified completion provider is not supported")


@backend.route("/register", methods=["POST"])
def register():
    # return not_implemented_error
    return jsonify({"error": "Not yet implemented"}), 405


@backend.route("/login", methods=["POST"])
def login():
    # return not_implemented_error
    return jsonify({"error": "Not yet implemented"}), 405


@backend.route("/past_chats", methods=["GET"])
def get_histories():
    # return not_implemented_error
    return jsonify({"error": "Not implemented yet"})


@backend.route("/chat_history", methods=["GET"])
def get_chat_history():
    # return not_implemented_error
    return jsonify({"error": "Not yet implemented"}), 405


@backend.route("/send_message", methods=["POST"])
def send_message():
    data = request.get_json()

    if data is None or "messages" not in data.keys():
        return jsonify({"error": "No user prompt received"}), 400

    else:
        logger.debug(f"Received request: {data['messages']}")
        try:
            # TODO fix this kludge - why is the model failing to encode if
            # I don't do this?
            full_message = " ".join(
                [message["content"] for message in data["messages"]]
            )
            contexts = vector_db.get_nearest(3, full_message)
            for context in contexts:
                logger.debug(f"Received context: {context}")

            logger.debug("Querying provider")
            provide_res = provider.request(contexts, data["messages"])

            return Response(
                stream_with_context(provide_res),
                mimetype="text/event-stream",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
            )

        except Exception as e:
            logger.error(f"Error in chat stream: {str(e)}")
            return jsonify({"error": "Error reaching chatbot"}), 500


@backend.route("/example_page", methods=["GET"])
def get_example():
    return jsonify({"key": "value"}), 200


# print(__name__)
if __name__ == "__main__":
    # app.run()
    backend.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))


# def lambda_handler(event, context):
#     print(f"Received event: {event}")
#     print(f"Received context: {context}")
#     return awsgi.response(backend, event, context)
