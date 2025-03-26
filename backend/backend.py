from flask import Flask, Response, json, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
from typing import Iterable, cast

import openai
from openai.types.chat import ChatCompletionMessageParam
from werkzeug.wrappers import response

app = Flask(__name__)

load_dotenv()

# app.secret_key = "change_this_key"  # TODO
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise ValueError("Could not initialize SECRET_KEY for flask")

api_key = os.environ.get("API_KEY", "fake_key")
app.config["api_key"] = api_key

CORS(app)

base_url = os.environ.get("BASE_URL")
if not base_url:
    raise ValueError("Could not find the url of the LLM server")

model_name = os.environ.get("MODEL")

if model_name is not None:
    model = model_name
else:
    raise ValueError("Could not find the name of the model")


system_prompt: ChatCompletionMessageParam = {
    "role": "assistant",
    "content": "You are a helpful assistant that assists users with the video game Minecraft. Respond to the user's query.",
}

# model = os.environ.get("MODEL")
# if not model:
#     raise ValueError("Could not find the name of the model")

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
    # return jsonify({"error": "Not yet implemented"}), 405
    data = request.get_json()

    if data is None or "messages" not in data.keys():
        return jsonify({"error": "No user prompt received"}), 400

    else:
        try:
            messages: Iterable[ChatCompletionMessageParam] = []

            messages.append(system_prompt)

            for message in data["messages"]:
                # app.logger.info(f"Received message: {message}")
                new_message: ChatCompletionMessageParam = {
                    "role": message["role"],
                    "content": message["content"],
                }

                messages.append(new_message)

            # new_message: ChatCompletionMessageParam = {
            #     "role": "user",
            #     "content": request.json["message"],
            # }

            # messages = [system_prompt, new_message]
            #
            def generate():
                response = client.chat.completions.create(
                    messages=messages,
                    model=model,
                    stream=True,
                    max_completion_tokens=16,
                    max_tokens=16,
                )

                for chunk in response:
                    # if 'content' in chunk.choices[0].delta:
                    #     content = chunk.choices[0].delta.content
                    #
                    #     yield f'data: {json.dumps({'content': content})}\n\n'
                    content = chunk.choices[0].delta.content
                    app.logger.info(f"Sending token {content}")
                    yield f"data: {json.dumps({'content': content})}\n\n"

            return Response(generate(), mimetype="text/event-stream")

            # chat_completion = client.chat.completions.create(
            #     messages=messages,
            #     model=model,
            #     # stream=True,
            #     max_completion_tokens=16,
            #     max_tokens=16,
            # )
            #
            # return jsonify({"response": chat_completion.choices[0].message.content})

        except Exception as e:
            # print(e)
            app.logger.error(f"Error in chat stream: {str(e)}")
            return jsonify({"error": "Error reaching chatbot"}), 500
    return jsonify({"response": "Chat bot is not currently running"}), 200


@app.route("/example_page", methods=["GET"])
def get_example():
    return jsonify({"key": "value"}), 200


if __name__ == "__main__":
    app.run(debug=True)
