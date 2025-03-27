from backend.providers.provider import Provider
import openai


class Llama(Provider):
    def __init__(
        self,
        client: openai.OpenAI,
        system_prompt: str = "You are a helpful assistant, who helps users with problems related to the game Minecraft",
    ) -> None:
        super().__init__()
        self.client = client
        self._system_prompt = system_prompt

    def request(self, messages: list[str]) -> None:
        # return super().request(messages)
        pass

        def generate():
            pass

    def system_prompt(self) -> str:
        return self._system_prompt
