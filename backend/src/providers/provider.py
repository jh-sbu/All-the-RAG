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
        self,
        messages: list[dict[str, str]],
        # ) -> Generator[tuple[str, str], None, None]:
    ) -> str:
        """
        Use this provider to generate a chat title for a given chat session
        Unlike chat completions, there is no real user expectation that this
        completes in real time, so I don't need to forward the individual chunks
        to the client in real time and can compile them on the backend
        """
        raise NotImplementedError

    @abc.abstractmethod
    def system_prompt(self, prompt: str):
        """
        Set the system prompt
        """
        raise NotImplementedError

    @abc.abstractmethod
    def title_prompt(self, prompt: str):
        """
        Set the system prompt used for the titling agent that creates a title for the chat interaction
        """
