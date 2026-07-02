from ai_core import build_provider


class SummarizationAgent:
    def __init__(self, provider_name: str, openai_api_key: str | None, model: str) -> None:
        self._provider = build_provider(
            provider_name=provider_name, api_key=openai_api_key, model=model
        )

    def run(self, text: str) -> str:
        return self._provider.summarize(text)
