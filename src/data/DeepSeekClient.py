from src.core.ILLMClient import ILLMClient
from typing import Any
import httpx
from src.core.LLMConfig import LLMConfig


class DeepSeekClient(ILLMClient):
    def __init__(self, llm_config: LLMConfig):
        if not llm_config.is_configured:
            raise ValueError("LLMConfig не сконфигурирован правильно")
        self.config = llm_config

    async def chat(self,
                   prompt: str,
                   system_message: str = "You are a helpful assistant",
                   temperature: float = 0.6,
                   max_tokens: int = 512) -> str:
        if not prompt.strip():
            raise ValueError("Промпт не может быть пустым")

        headers = {"Authorization": f"Bearer {self.config.api_key}"}

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": max(0.1, min(temperature, 2.0)),
            "max_tokens": max(1, min(max_tokens, 4096)),
            "stream": False
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.config.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()

                if "choices" not in data or not data["choices"]:
                    raise ValueError("Некорректный формат ответа от API")

                return data["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP ошибка: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise Exception(f"Ошибка соединения: {e}")
        except KeyError as e:
            raise ValueError(f"Некорректный формат ответа: отсутствует ключ {e}")

    def get_model_info(self) -> dict[str, Any]:
        return {
            "model": self.config.model,
            "base_url": self.config.base_url,
            "api_key_configured": bool(self.config.api_key),
        }
