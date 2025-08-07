import abc

from flask import Response


class Provider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def request(self, contexts: list[str], messages: list[dict[str, str]]) -> Response:
        raise NotImplementedError

    @abc.abstractmethod
    def system_prompt(self, prompt: str):
        """
        Set the system prompt
        """
        raise NotImplementedError
