import abc
from typing import Generator

from models.context import Context


class Provider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def request(
        self, contexts: list[Context], messages: list[dict[str, str]]
    ) -> Generator[tuple[str, str], None, None]:
        """
        Send a request to whatever provider is configured by the environment and
        stream back the results
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_chat_title(
        self, contents: list[dict[str, str]]
    ) -> Generator[tuple[str, str], None, None]:
        """
        Use this provider to generate a chat title for a given chat session
        """
        raise NotImplementedError

    @abc.abstractmethod
    def system_prompt(self, prompt: str):
        """
        Set the system prompt
        """
        raise NotImplementedError
