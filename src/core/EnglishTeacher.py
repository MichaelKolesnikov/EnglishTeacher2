from src.core.ILLMClient import ILLMClient
from src.core.IUserRepository import IUserRepository


class EnglishTeacher:
    def __init__(self, user_repository: IUserRepository, llm_client: ILLMClient):
        self.user_repository: IUserRepository = user_repository
        self.llm_client: ILLMClient = llm_client
        self.prompt_divider = "\n---\n"

    async def get_answer(self, user_id: int, user_message: str) -> str:
        self.user_repository.add_new_message(user_id, user_message, str(user_id))
        await self._update_memory_about_user(user_id)
        new_level = self._update_level(user_id)
        prompt = ""
        with open("prompt/base_prompt.md") as f:
            prompt = f.read() + self.prompt_divider
        if isinstance(new_level, str):
            with open("prompt/level_was_updated_prompt.md") as f:
                prompt += f.read() + "# New level:\n" + new_level + self.prompt_divider
        history = self.user_repository.get_history(user_id)
        prompt += "# History:\n" + history + self.prompt_divider
        return await self.llm_client.get_answer(prompt)

    async def _update_memory_about_user(self, user_id: int) -> None:
        history = self.user_repository.get_history(user_id)
        current_memory = self.user_repository.get_memory(user_id)
        with open("prompt/update_memory_prompt.md") as f:
            update_memory_prompt = f.read()
        new_memory = await self.llm_client.get_answer(
            update_memory_prompt + "# History:\n" + history + "# Current memory:\n" + current_memory)
        if new_memory:
            self.user_repository.set_memory(user_id, new_memory)

    async def _update_level(self, user_id: int) -> str | None:
        history = self.user_repository.get_history(user_id)
        current_level = self.user_repository.get_user_level(user_id)
        with open("prompt/update_level_prompt.md") as f:
            update_level_prompt = f.read()
        new_level = await self.llm_client.get_answer(update_level_prompt + "\n" + current_level + "\n" + history)
        if new_level:
            self.user_repository.set_user_level(user_id, new_level)
            return new_level
        return None
