import abc
from typing import Generator

from models.context import Context


class Provider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def request(
        self, contexts: list[Context], messages: list[dict[str, str]]
    ) -> Generator[str, None, None]:
        """
        Send a request to whatever provider is configured by the environment and
        stream back the results
        """
        raise NotImplementedError

    @abc.abstractmethod
    def system_prompt(self, prompt: str):
        """
        Set the system prompt
        """
        raise NotImplementedError
