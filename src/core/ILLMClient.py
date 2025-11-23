from abc import ABC, abstractmethod
from typing import Any


class ILLMClient(ABC):
    @abstractmethod
    async def chat(self,
                   prompt: str,
                   system_message: str = "You are a helpful assistant",
                   temperature: float = 0.6,
                   max_tokens: int = 512) -> str:
        pass

    @abstractmethod
    def get_model_info(self) -> dict[str, Any]:
        pass