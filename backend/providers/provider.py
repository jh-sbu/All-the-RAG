import abc


class Provider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def request(self, messages: list[str]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def system_prompt(self) -> str:
        raise NotImplementedError
