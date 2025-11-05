import logging
import os
from typing import Generator, Iterable
from dotenv import load_dotenv
from flask import Response, json, stream_with_context
import openai
from openai.types.chat import ChatCompletionMessageParam

from models.context import Context
from providers.provider import Provider


def get_model_name():
    completion_model_name = os.environ.get("COMPLETION_MODEL")
    if completion_model_name is None:
        raise ValueError("Could not find the name of the model for OpenRouter")

    return completion_model_name


def get_client() -> openai.OpenAI:
    base_url = os.environ.get("BASE_URL")
    if base_url is None:
        raise ValueError("Could not find the base url for OpenRouter")

    api_key = os.environ.get("API_KEY")
    if api_key is None:
        raise ValueError("Could not read API key for OpenRouter")

    # Don't need an api key for local inference
    return openai.OpenAI(api_key=api_key, base_url=base_url)


class OpenRouter(Provider):
    def __init__(
        self,
        system_prompt: str = "You are a helpful assistant, who helps users with problems related to the game Minecraft",
        log_level: int = logging.INFO,
    ) -> None:
        super().__init__()
        load_dotenv()

        self.model = get_model_name()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

        self.client = get_client()

        self.logger.debug(f"Provider client: {self.client}")
        self._system_prompt: ChatCompletionMessageParam = {
            "role": "system",
            "content": system_prompt,
        }

    def request(
        self, contexts: list[Context], messages: list[dict[str, str]]
    ) -> Generator[str, None, None]:
        self.logger.debug(
            f"Received request with {len(contexts)} contexts and {len(messages)} messages"
        )
        chat_messages: Iterable[ChatCompletionMessageParam] = []

        chat_messages.append(self._system_prompt)

        for context in contexts:
            new_message: ChatCompletionMessageParam = {
                "role": "user",
                "content": "Context: " + context.content,
            }
            chat_messages.append(new_message)

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

        self.logger.debug("Finished preparing request to provider")

        def generate():
            source_list = [
                {"title": "Not provided", "summary": "No summary", "url": context.url}
                for context in contexts
            ]
            self.logger.debug(f"Source list with {len(source_list)} items prepared")
            yield f"event: update_sources\ndata: {json.dumps({'sources': source_list})}\n\n"
            self.logger.debug("Yielded sources")

            response = self.client.chat.completions.create(
                messages=chat_messages,
                model=self.model,
                stream=True,
                max_completion_tokens=1024,
                max_tokens=1024,
            )

            for chunk in response:
                content = chunk.choices[0].delta.content
                self.logger.debug(f"New content: {content}")
                # if content != "":
                yield f"event: new_chunk\ndata: {json.dumps({'content': content})}\n\n"

        return generate()

    def system_prompt(self, prompt: str) -> None:
        self._system_prompt: ChatCompletionMessageParam = {
            "role": "system",
            "content": prompt,
        }
