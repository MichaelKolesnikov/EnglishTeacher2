import asyncio
import json
from datetime import datetime
from pathlib import Path
from src.core.ILLMLogger import ILLMLogger
from typing import Any


class JsonLlmLogger(ILLMLogger):
    def __init__(self, log_dir: str = "logs/llm_requests"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / f"llm_{datetime.now():%Y%m%d}.jsonl"
        self._lock = asyncio.Lock()

    async def log_request(
            self,
            prompt: str | list[dict[str, str]],
            response: str,
            temperature: float,
            model_info: dict[str, Any],
            metadata: dict[str, Any] | None = None
    ) -> None:
        async with self._lock:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "temperature": temperature,
                "model": model_info.get("model"),
                "base_url": model_info.get("base_url"),
                "prompt": prompt if isinstance(prompt, str) else prompt,
                "response": response.strip(),
                **(metadata or {})
            }

            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

            print("\n" + "=" * 60)
            print(f"LLM REQUEST | {log_entry['timestamp']} | temp={temperature}")
            print(f"Model: {model_info.get('model')}")
            if metadata:
                print(f"Context: {metadata}")
            print("-" * 60)
            print("PROMPT:")
            if isinstance(prompt, str):
                print(prompt.strip())
            else:
                for msg in prompt:
                    print(f"{msg['role'].upper()}: {msg['content'][:500]}{'...' if len(msg['content']) > 500 else ''}")
            print("-" * 60)
            print("RESPONSE:")
            print(response.strip())
            print("=" * 60 + "\n")
