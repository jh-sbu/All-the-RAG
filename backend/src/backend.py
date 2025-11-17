import json
import uuid
from flask import Flask, Response, jsonify, request, stream_with_context
from flask_cors import CORS

import jwt

from authlib.integrations.flask_client import OAuth

from dotenv import load_dotenv
import os

import requests
from sqlalchemy import Uuid
from sqlalchemy import exc
from sqlalchemy.exc import IntegrityError, NoResultFound

from atr_logger import get_logger, set_log_level
from db.database import (
    add_example_message_to_chat,
    add_test_user,
    create_example_chat,
    db_create_chat,
    db_delete_chat,
    db_get_all_chats,
    db_get_all_messages,
    db_get_user,
    db_get_chat,
    db_create_message,
)
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


logger = get_logger()
set_log_level(log_level)


backend.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
if not backend.config["SECRET_KEY"]:
    raise ValueError("Could not initialize SECRET_KEY for flask")

oauth = OAuth(backend)

if False:
    google = oauth.register(
        name="google",
        client_id="CLIENT_ID",
        client_secret="CLIENT_SECRET",
        server_metadata_url="GOOGLE_URL",
        client_kwargs={"scope": "openid email"},
    )

# Some hosts, e.g. AWS lambda urls, do CORS themselves; turn on/off
# flask's own cors depending on whether it is needed or not
use_cors = os.environ.get("USE_CORS", None)
if use_cors is not None:
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

database_url = os.environ.get("DATABASE_URL", "sqlite+pysqlite:///example.db")

logger.info(f"VDB provider read as: {vdb_provider}")
logger.info(f"Created vector db interface of type {type(vector_db)}")

system_prompt = "You are a helpful assistant that assists users with the All the Mods modpacks for the video game Minecraft. Another model will provide you with whatever context it can about the user's query. Read the provided context and use it to respond to the user's query. Do not accuse the user of being the one to provide you with the contexts - it is another bot that does that and users do not like being accused of things they didn't do. Be concise - your job is to find the relevant information in the given context, not repeat everything you see word for word."

completion_provider = os.environ.get("COMPLETION_PROVIDER")
logger.info(f"Setting up completion provider {completion_provider}")
if completion_provider is None:
    raise ValueError("Could not find completion provider configuration")
elif completion_provider == "Local":
    provider = Llama(system_prompt=system_prompt)
elif completion_provider == "OpenRouter":
    provider = OpenRouter(system_prompt=system_prompt)
else:
    raise ValueError("Specified completion provider is not supported")


# TODO - Remove this when testing is done!
test_user_email = "test_email@example.com"


@backend.route("/register", methods=["POST"])
def register():
    # return not_implemented_error
    return jsonify({"error": "Not yet implemented"}), 405


@backend.route("/login", methods=["POST"])
def login():
    # return not_implemented_error
    return jsonify({"error": "Not yet implemented"}), 405


@backend.route("/auth/callback", methods=["POST"])
def auth_callback():
    req_json = request.json
    if req_json is not None:
        code = req_json.get("code")
        code_verifier = req_json.get("code_verifier")

        token_response = requests.post(
            "GOOGLE_OATH_URL",
            data={
                "client_id": "YOUR_CLIENT_ID",
                "client_secret": "YOUR_CLIENT_SECRET",
                "code": code,
                "code_verifier": code_verifier,
                "redirect_uri": "YOUR_FRONTEND_URI?",
                "grant_type": "authorization_code",
            },
        )

        tokens = token_response.json()

        user_info = jwt.decode(tokens["id_token"], options={"verify_signature": False})

    if False:
        return jsonify({"error": "Could not read json from request"}), 400

    return jsonify({"error": "Not yet implemented"}), 405


@backend.route("/api/user", methods=["DELETE"])
def delete_account():
    logger.warning("WARNING: NOT ACTUALLY IMPLEMENTED!")
    # return not_implemented_error
    return jsonify({"error": "Not yet implemented"}), 405


@backend.route("/api/chat", methods=["GET"])
def get_chat_history():
    logger.warning("WARNING! WARNING! Test user account enabled!")
    user_email = "test_email@example.com"

    try:
        chats = db_get_all_chats(db_url=database_url, user_email=user_email)

        return jsonify({"chats": chats})

    except NoResultFound:
        return jsonify({"error": "Invalid user"}), 404


@backend.route("/api/chat/<uuid:chat_id>", methods=["GET"])
def get_chat_messages(chat_id):
    logger.warning("WARNING! WARNING! Test user account enabled!")
    user_email = test_user_email

    try:
        messages = db_get_all_messages(
            db_url=database_url, chat_id=chat_id, user_email=user_email
        )

        for message in messages:
            print(f"Message: {message}")

        return jsonify({"messages": messages})

    except PermissionError:
        logger.info(
            f"User {user_email} attempted to access chat {chat_id} but is NOT the owner of that chat"
        )
        # Don't tell them they found one though
        return jsonify({"error": "Could not locate the specified record"}), 404
    except NoResultFound:
        return jsonify({"error": "Could not locate the specified record"}), 404


@backend.route("/api/chat", methods=["DELETE"])
def delete_chat():
    chat_id = request.args.get("chat_id")

    user_email = test_user_email

    logger.info(f"User {user_email} attempting to delete chat {chat_id}")

    if not chat_id:
        return jsonify({"error": "No chat ID specified"}), 400

    try:
        chat_id = uuid.UUID(chat_id)
    except ValueError:
        return jsonify({"error": "Could not parse chat ID"}), 400

    try:
        db_delete_chat(database_url, chat_id=chat_id, user_email=user_email)
    except IntegrityError:
        return jsonify({"error": "Error updating database"}), 500
    except NoResultFound:
        return jsonify({"error": "Could not locate the specified record"}), 404
    except PermissionError:
        logger.info(
            f"User {user_email} attempted to delete chat {chat_id} but is NOT the owner of that chat"
        )
        # Don't want to allow enumerating existing chats so return the same as though
        # the record wasn't found, but we do want to log this seperately to spot
        # bad behavior more easily
        return jsonify({"error": "Could not locate the specified record"}), 404

    return "ok", 200


@backend.route("/api/message", methods=["POST"])
def send_message():
    data = request.get_json()

    # TODO
    try:
        user = db_get_user(database_url, test_user_email)
    except NoResultFound:
        user = None

    if data is None or "messages" not in data.keys():
        return jsonify({"error": "No user prompt received"}), 400

    if "uuid" not in data.keys():
        return jsonify(
            {
                "error": "uuid field not received in request (new chats should report uuid as None)"
            }
        ), 400

    chat_uuid = data["uuid"]
    messages = data.get("messages")
    if not isinstance(messages, list) or len(messages) < 1:
        return jsonify({"error": "messages must be a non-empty list"}), 400

    full_message = " ".join([message["content"] for message in messages])

    # full_message = " ".join([message["content"] for message in data["messages"]])
    latest_message = messages[-1]["content"]
    logger.debug(f"User message: {full_message}")

    logger.debug(f"Latest message: {latest_message}")

    try:
        if user is not None:
            # New chat
            if chat_uuid == "None":
                logger.debug(
                    "Received post request with no chat_uuid, creating new one"
                )
                chat = db_create_chat(database_url, full_message, user)
                if chat is None:
                    return jsonify({"error": "Failed to save user chat"}), 500

                chat_uuid = chat.id

            # Double check to make sure this is an existing chat
            else:
                logger.debug(
                    f"Received post request with uuid {chat_uuid}, verifying access"
                )
                try:
                    chat = db_get_chat(database_url, chat_uuid, test_user_email)
                    chat_uuid = chat.id

                except PermissionError:
                    logger.warning(
                        f"User {test_user_email} attempted to access chat {chat_uuid}, which is a real chat, but not theirs"
                    )
                    return jsonify({"error": "Record not found"}), 404

                except NoResultFound:
                    return jsonify({"error": "Record not found"}), 404

                db_create_message(
                    database_url,
                    "user",
                    latest_message,
                    chat_uuid,
                )

        contexts = vector_db.get_nearest(3, full_message)
        logger.debug(f"Received {len(contexts)} context(s)")

        logger.debug("Querying provider")

        def stream_and_store():
            # Pyright understands chat_uuid is not "None" if user
            # is not None, if we check chat_uuid here it complains
            # about chat_uuid below in the finally block
            if data["uuid"] == "None" and user is not None:
                yield f"event: set_uuid\ndata: {json.dumps({'new_uuid': str(chat_uuid)})}\n\n"

            chunks: list[str] = []

            try:
                for event in provider.request(contexts, data["messages"]):
                    if event[0] == "new_chunk" and event[1] != "":
                        chunks.append(event[1])
                        yield f"event: {event[0]}\ndata: {json.dumps({'content': event[1]})}\n\n"
                    elif event[0] == "update_sources":
                        yield f"event: {event[0]}\ndata: {event[1]}\n\n"

            finally:
                message_content = "".join(chunks)
                logger.info(f"Received message: {message_content}")
                if user is not None:
                    db_create_message(
                        database_url,
                        "assistant",
                        message_content,
                        chat_uuid,
                        # uuid.UUID("07768b7e-c3f0-40f4-a84d-7706d0d425e5"),
                    )

                # TODO
                logger.warning("WARNING! WARNING! UPLOADING TO DB NOT YET SUPPORTED!")
                logger.warning("WARNING! WARNING! UPLOADING TO DB NOT YET SUPPORTED!")
                logger.warning("(It still just uses the test user!)")

        return Response(
            stream_with_context(stream_and_store()),
            mimetype="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )

    except Exception as e:
        logger.error(f"Error in chat stream: {str(e)}")
        return jsonify({"error": "Error reaching chatbot"}), 500


@backend.route("/health_check", methods=["GET"])
def health_check():
    return "ok", 200


@backend.route("/test/add_test_user", methods=["GET"])
def test_add_test_user():
    return add_test_user(database_url)


@backend.route("/test/create_example_chat", methods=["GET"])
def test_create_example_chat():
    return create_example_chat(database_url)


@backend.route("/test/add_example_message_to_chat", methods=["GET"])
def test_add_example_message_to_chat():
    return add_example_message_to_chat(database_url)


# print(__name__)
# if __name__ == "__main__":
#     # app.run()
#     backend.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))


if __name__ == "__main__":
    # print(f"Database URL: {database_url}")
    logger.info(f"Database URL: {database_url}")
    backend.run()
