import os
from typing import Iterable
from dotenv import load_dotenv
from flask import Response, json
from openai.types.chat import ChatCompletionMessageParam
from providers.provider import Provider
import openai


def get_model_name():
    model_name = os.environ.get("MODEL")
    if model_name is None:
        raise ValueError("Could not find the name of the model for local inference")

    return model_name


def get_client() -> openai.OpenAI:
    base_url = os.environ.get("BASE_URL")
    if base_url is None:
        raise ValueError("Could not find the base url for local inference")

    # Don't need an api key for local inference
    return openai.OpenAI(api_key="FAKE_KEY", base_url=base_url)


class Llama(Provider):
    def __init__(
        self,
        system_prompt: str = "You are a helpful assistant, who helps users with problems related to the game Minecraft",
    ) -> None:
        super().__init__()
        load_dotenv()
        self.client = get_client()
        self._system_prompt: ChatCompletionMessageParam = {
            "role": "system",
            "content": system_prompt,
        }

        self.model = get_model_name()

    def request(self, messages: list[dict[str, str]]) -> Response:
        chat_messages: Iterable[ChatCompletionMessageParam] = []

        chat_messages.append(self._system_prompt)

        for message in messages:
            # LSP wants to ensure a literal is used here
            if message["role"] == "assistant":
                new_message: ChatCompletionMessageParam = {
                    "role": "assistant",
                    "content": message["content"],
                }
            else:
                new_message: ChatCompletionMessageParam = {
                    "role": "user",
                    "content": message["content"],
                }

            chat_messages.append(new_message)

        def generate():
            response = self.client.chat.completions.create(
                messages=chat_messages,
                model=self.model,
                stream=True,
                max_completion_tokens=16,
                max_tokens=16,
            )

            for chunk in response:
                content = chunk.choices[0].delta.content
                yield f"data: {json.dumps({'content': content})}\n\n"

        return Response(generate(), mimetype="text/event-stream")

    def system_prompt(self, prompt: str) -> None:
        self._system_prompt: ChatCompletionMessageParam = {
            "role": "system",
            "content": prompt,
        }
