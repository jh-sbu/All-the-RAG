import abc


class Provider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def request(self, request_text: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def system_prompt(self) -> str:
        raise NotImplementedError
