from typing import Optional


class LLMConfig:
    def __init__(
            self,
            api_key: Optional[str] = None,
            base_url: Optional[str] = None,
            model: Optional[str] = None
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    def __str__(self) -> str:
        return f"LLMConfig(base_url='{self.base_url}', model='{self.model}')"

    def __repr__(self) -> str:
        return f"LLMConfig(api_key='***', base_url='{self.base_url}', model='{self.model}')"

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)
