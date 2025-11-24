from abc import ABC, abstractmethod
from typing import Any


class ILLMClient(ABC):
    @abstractmethod
    async def get_answer(self, prompt: str, temperature: float = 0.3) -> str:
        pass

    @abstractmethod
    def get_model_info(self) -> dict[str, Any]:
        pass
