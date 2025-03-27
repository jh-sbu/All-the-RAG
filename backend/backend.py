from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os

from providers.openrouter import OpenRouter
from providers.llama_server import Llama

app = Flask(__name__)

load_dotenv()

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise ValueError("Could not initialize SECRET_KEY for flask")

CORS(app)

system_prompt = "You are a helpful assistant that assists users with the video game Minecraft. Respond to the user's query."

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
            return provider.request(data["messages"])

            # messages: Iterable[ChatCompletionMessageParam] = []
            #
            # messages.append(system_prompt)
            #
            # for message in data["messages"]:
            #     # app.logger.info(f"Received message: {message}")
            #     new_message: ChatCompletionMessageParam = {
            #         "role": message["role"],
            #         "content": message["content"],
            #     }
            #
            #     messages.append(new_message)
            #
            # def generate():
            #     response = client.chat.completions.create(
            #         messages=messages,
            #         model=model,
            #         stream=True,
            #         max_completion_tokens=16,
            #         max_tokens=16,
            #     )
            #
            #     for chunk in response:
            #         content = chunk.choices[0].delta.content
            #         app.logger.info(f"Sending token {content}")
            #         yield f"data: {json.dumps({'content': content})}\n\n"
            #
            # return Response(generate(), mimetype="text/event-stream")

        except Exception as e:
            app.logger.error(f"Error in chat stream: {str(e)}")
            return jsonify({"error": "Error reaching chatbot"}), 500


@app.route("/example_page", methods=["GET"])
def get_example():
    return jsonify({"key": "value"}), 200


if __name__ == "__main__":
    app.run(debug=True)
