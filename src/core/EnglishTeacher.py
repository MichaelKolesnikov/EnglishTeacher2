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
            "The student made no grammar or vocabulary mistake in the last message. "
            "Just continue the conversation naturally in English.",

            "The student made a new mistake. The exact wrong phrase is: \"{mistake}\"\n"
            "Gently hint at the correct form or use the correct version naturally in your reply. "
            "Do it in English only. Never point out the mistake directly.",

            "The student repeated the exact same mistake again: \"{mistake}\"\n"
            "Now briefly explain the rule in Russian (1–2 sentences max), then immediately switch back to English "
            "and continue the conversation normally."
        ]

    async def get_answer(self, user_id: int, user_message: str) -> str:
        self.user_repository.add_new_message(user_id, user_message, str(user_id))
        await self._update_memory_about_user(user_id)
        new_level = await self._update_level(user_id)

        mistake, is_second = await self._get_mistakes_and_is_it_second(user_message, self.user_repository.get_mistake(user_id))
        if mistake:
            self.user_repository.set_correction_state(user_id, 1 + is_second)
        else:
            self.user_repository.set_correction_state(user_id, 0)
        self.user_repository.set_mistake(user_id, mistake)

        prompt = self.base_prompt + self.prompt_divider
        prompt += self.correction_prompt[self.user_repository.get_correction_state(user_id)].replace("{mistake}", mistake) + self.prompt_divider
        if isinstance(new_level, str):
            prompt += self.level_was_updated_prompt + "# New level:\n" + new_level + self.prompt_divider
        history = self.user_repository.get_history(user_id)
        prompt += "# History:\n" + history + self.prompt_divider
        answer = await self.llm_client.get_answer(prompt, temperature=0.6)
        self.user_repository.add_new_message(user_id, answer, "")
        return answer

    async def _update_memory_about_user(self, user_id: int) -> None:
        history = self.user_repository.get_history(user_id)
        current_memory = self.user_repository.get_memory(user_id)
        new_memory = await self.llm_client.get_answer(self.update_memory_prompt + "# History:\n" + history + "# Current memory:\n" + current_memory, temperature=0.5)
        if new_memory:
            self.user_repository.set_memory(user_id, new_memory)

    async def _update_level(self, user_id: int) -> str | None:
        history = self.user_repository.get_history(user_id)
        current_level = self.user_repository.get_user_level(user_id)
        new_level = await self.llm_client.get_answer(self.update_level_prompt + "\n" + current_level + "\n" + history)
        if new_level and new_level != current_level:
            self.user_repository.set_user_level(user_id, new_level)
            return new_level
        return None

    async def _get_mistakes_and_is_it_second(self, user_message: str, prev_mistake: str) -> tuple[str, bool]:
        mistake = await self.llm_client.get_answer(self.check_prompt + "# Message:\n" + user_message + self.prompt_divider + "# Previous mistake:\n" + prev_mistake)
        flag = "SECOND"
        if mistake.startswith(flag):
            return mistake[len(flag):], True
        return mistake, False
