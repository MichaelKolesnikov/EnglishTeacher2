from abc import ABC, abstractmethod
from typing import Any


class ILLMLogger(ABC):
    @abstractmethod
    async def log_request(
            self,
            prompt: str | list[dict[str, str]],
            response: str,
            temperature: float,
            model_info: dict[str, Any],
            metadata: dict[str, Any] | None = None
    ) -> None:
        pass
