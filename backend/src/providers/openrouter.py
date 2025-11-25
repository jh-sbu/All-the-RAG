import logging
import os
from typing import Generator, Iterable
from dotenv import load_dotenv
from flask import json
import openai
from openai.types.chat import ChatCompletionMessageParam

from atr_logger import get_logger
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

    return openai.OpenAI(api_key=api_key, base_url=base_url)


logger = get_logger()


class OpenRouter(Provider):
    def __init__(
        self,
        system_prompt: str = "You are a helpful assistant, who helps users with problems related to the game Minecraft",
        title_prompt: str = "Create a title that summarizes the following interaction",
    ) -> None:
        super().__init__()
        # load_dotenv()

        self.model = get_model_name()

        self.client = get_client()

        logger.debug(f"Provider client: {self.client}")
        self._system_prompt: ChatCompletionMessageParam = {
            "role": "system",
            "content": system_prompt,
        }

        self._title_prompt: ChatCompletionMessageParam = {
            "role": "system",
            "content": title_prompt,
        }

    def get_chat_title(
        self,
        user_query: str,
        agent_response: str,
    ) -> str:
        # TODO
        """Messages should be one user message, one assistant message
        I can't make these ChatCompletionMessageParam because
        backend.py should be agnostic to model provider, including
        providers that don't use OpenAI API
        """
        logger.debug("Generating chat title for new chat")

        user_message: ChatCompletionMessageParam = {
            "role": "user",
            "content": user_query,
        }

        agent_message: ChatCompletionMessageParam = {
            "role": "assistant",
            "content": agent_response,
        }

        chat_messages: Iterable[ChatCompletionMessageParam] = [
            self._title_prompt,
            user_message,
            agent_message,
        ]

        # for message in messages:
        #     if message["role"] == "assistant":
        #         new_message: ChatCompletionMessageParam = {
        #             "role": "user",
        #             "content": message["content"],
        #         }
        #     else:
        #         new_message: ChatCompletionMessageParam = {
        #             "role": "assistant",
        #             "content": message["content"],
        #         }
        #
        #     chat_messages.append(new_message)

        response = self.client.chat.completions.create(
            messages=chat_messages,
            model=self.model,
            stream=True,
            max_completion_tokens=1024,
            max_tokens=1024,
        )

        title = "".join(
            [
                chunk.choices[0].delta.content
                for chunk in response
                if chunk.choices[0].delta.content is not None
                and chunk.choices[0].delta.content != ""
            ]
        )

        return title

    def request(
        self, contexts: list[Context], messages: list[dict[str, str]]
    ) -> Generator[tuple[str, str], None, None]:
        logger.debug(
            f"Received request with {len(contexts)} contexts and {len(messages)} messages"
        )
        chat_messages: Iterable[ChatCompletionMessageParam] = [self._system_prompt]

        # chat_messages.append(self._system_prompt)

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

        logger.debug("Finished preparing request to provider")

        def generate():
            source_list = [
                {"title": "Not provided", "summary": "No summary", "url": context.url}
                for context in contexts
            ]
            logger.debug(f"Source list with {len(source_list)} items prepared")
            # yield f"event: update_sources\ndata: {json.dumps({'sources': source_list})}\n\n"
            yield "update_sources", json.dumps({"sources": source_list})
            logger.debug("Yielded sources")

            response = self.client.chat.completions.create(
                messages=chat_messages,
                model=self.model,
                stream=True,
                max_completion_tokens=1024,
                max_tokens=1024,
            )

            for chunk in response:
                content = chunk.choices[0].delta.content
                if content is None:
                    content = ""
                yield "new_chunk", content

        return generate()

    def system_prompt(self, prompt: str) -> None:
        self._system_prompt: ChatCompletionMessageParam = {
            "role": "system",
            "content": prompt,
        }

    def title_prompt(self, prompt: str) -> None:
        self._title_prompt: ChatCompletionMessageParam = {
            "role": "system",
            "content": prompt,
        }
