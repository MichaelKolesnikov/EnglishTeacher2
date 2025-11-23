from abc import ABC, abstractmethod
from typing import Any


class ILLMClient(ABC):
    @abstractmethod
    async def chat(self, prompt: str) -> str:
        pass

    @abstractmethod
    def get_model_info(self) -> dict[str, Any]:
        pass
