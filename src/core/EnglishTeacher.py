from src.core.ILLMClient import ILLMClient
from src.core.IUserRepository import IUserRepository


class EnglishTeacher:
    def __init__(self, user_repository: IUserRepository, llm_client: ILLMClient):
        self.user_repository: IUserRepository = user_repository
        self.llm_client: ILLMClient = llm_client
        self.prompt_divider = "\n---\n"
        with open("src/core/prompt/base_prompt.md") as f:
            self.base_prompt = f.read()
        with open("src/core/prompt/level_was_updated_prompt.md") as f:
            self.level_was_updated_prompt = f.read()
        with open("src/core/prompt/update_memory_prompt.md") as f:
            self.update_memory_prompt = f.read()
        with open("src/core/prompt/update_level_prompt.md") as f:
            self.update_level_prompt = f.read()
        with open("src/core/prompt/check_prompt.md") as f:
            self.check_prompt = f.read()
        self.correction_prompt = [
            "Видно, что пользователь не допустил ошибки, просто продолжай диалог на английском.",
            "Видно, что пользователь допустил ошибку, однако, нужно его навести на то, где он ошибся, чтобы он исправил ошибку. Сделай это на английском, не переходя на русский",
            "Видно, что пользователь допустил ошибку не в первый раз, поэтому подскажи ему на русском, что не так."
        ]

    async def get_answer(self, user_id: int, user_message: str) -> str:
        self.user_repository.add_new_message(user_id, user_message, str(user_id))
        await self._update_memory_about_user(user_id)
        new_level = await self._update_level(user_id)

        mistakes = await self._get_mistakes(user_message)
        if mistakes:
            self.user_repository.set_correction_state(user_id, self.user_repository.get_correction_state(user_id) + 1)
        else:
            self.user_repository.set_correction_state(user_id, 0)

        prompt = self.base_prompt + self.prompt_divider
        prompt += self.correction_prompt[min(len(self.correction_prompt) - 1, self.user_repository.get_correction_state(user_id))] + self.prompt_divider
        if isinstance(new_level, str):
            prompt += self.level_was_updated_prompt + "# New level:\n" + new_level + self.prompt_divider
        history = self.user_repository.get_history(user_id)
        prompt += "# History:\n" + history + self.prompt_divider
        answer = await self.llm_client.get_answer(prompt)
        self.user_repository.add_new_message(user_id, answer, "")
        return answer

    async def _update_memory_about_user(self, user_id: int) -> None:
        history = self.user_repository.get_history(user_id)
        current_memory = self.user_repository.get_memory(user_id)
        new_memory = await self.llm_client.get_answer(self.update_memory_prompt + "# History:\n" + history + "# Current memory:\n" + current_memory)
        if new_memory:
            self.user_repository.set_memory(user_id, new_memory)

    async def _update_level(self, user_id: int) -> str | None:
        history = self.user_repository.get_history(user_id)
        current_level = self.user_repository.get_user_level(user_id)
        new_level = await self.llm_client.get_answer(self.update_level_prompt + "\n" + current_level + "\n" + history)
        if new_level:
            self.user_repository.set_user_level(user_id, new_level)
            return new_level
        return None

    async def _get_mistakes(self, user_message: str) -> str:
        return await self.llm_client.get_answer(self.check_prompt + "# Message:\n" + user_message)
