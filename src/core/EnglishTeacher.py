from src.core.ILLMClient import ILLMClient
from src.core.IUserRepository import IUserRepository
from src.core.TopicMaster import TopicMaster
from src.core.topics.registry import *


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

            "The student made a new mistake: \"{mistake}\"\n"
            "Gently hint at the correct form or use it naturally in your reply. "
            "Do it in English only. ",

            "The student repeated the same TYPE of mistake again: \"{mistake}\"\n"
            "Briefly explain the rule in Russian (1–2 short sentences, friendly tone), "
            "then immediately switch back to English and continue the conversation warmly."
        ]
        self.topic_master = TopicMaster(user_repository)
        self.message_counter = {}

    async def _detect_correct_topics_in_message(self, message: str) -> str:
        detect_prompt = f"""
    You are an expert topic detector.
    Return ONLY the topic keys (comma-separated, no spaces) if the student used them CORRECTLY and you are 100% sure.
    If nothing or unsure → return empty string.

    Available topics: {TOPIC_LIST}

    Student message: {message}

    Topics used correctly:
    """.strip()

        result = await self.llm_client.get_answer(detect_prompt, temperature=0.1)
        return result.strip()

    async def get_answer(self, user_id: int, user_message: str) -> str:
        self.user_repository.add_new_message(user_id, user_message, str(user_id))
        await self._update_memory_about_user(user_id)
        new_level = await self._update_level(user_id)

        prev_mistake = self.user_repository.get_mistake(user_id)
        mistake_raw, is_second = await self._get_mistakes_and_is_it_second(user_message, prev_mistake)
        mistake_text = ""

        if mistake_raw and mistake_raw != "NO_ERROR":
            parts = mistake_raw.split("||")
            mistake_text = parts[0].strip()
            if len(parts) >= 2:
                detected_topic_from_error = parts[1].strip()
                if detected_topic_from_error in TOPICS:
                    self.topic_master.register_usage(user_id, detected_topic_from_error, correct=False)

            if is_second:
                self.user_repository.set_correction_state(user_id, 2)
            else:
                self.user_repository.set_correction_state(user_id, 1)
        else:
            self.user_repository.set_correction_state(user_id, 0)

        self.user_repository.set_mistake(user_id, mistake_text)

        if not mistake_text:
            if user_id not in self.message_counter:
                self.message_counter[user_id] = 0
            self.message_counter[user_id] += 1

            if self.message_counter[user_id] % 4 == 0:
                used_topics = await self._detect_correct_topics_in_message(user_message)
                for topic_key in [t.strip() for t in used_topics.split(",") if t.strip()]:
                    if topic_key in TOPICS:
                        self.topic_master.register_usage(user_id, topic_key, correct=True)

        current_cefr = self.user_repository.get_user_level(user_id)
        next_topic_key = self.topic_master.get_next_topic(user_id, current_cefr)
        active_topic_line = ""
        if next_topic_key and next_topic_key in TOPICS:
            active_topic_line = f"# Active practice topic:\n{TOPICS[next_topic_key]['name']}\n" \
                                "Gently create a context where the student is very likely to use this grammar/vocabulary naturally. " \
                                "Do not mention the topic name directly.\n"

        prompt = self.base_prompt + self.prompt_divider

        correction_idx = self.user_repository.get_correction_state(user_id)
        prompt += self.correction_prompt[correction_idx].format(mistake=mistake_text or "") + self.prompt_divider

        if isinstance(new_level, str):
            prompt += self.level_was_updated_prompt.replace("{new_level}", new_level) + self.prompt_divider

        if active_topic_line:
            prompt += active_topic_line + self.prompt_divider

        history = self.user_repository.get_history(user_id)
        prompt += "# Conversation history (most recent at the bottom):\n" + history + self.prompt_divider
        answer = await self.llm_client.get_answer(prompt, temperature=0.3)
        self.user_repository.add_new_message(user_id, answer, "")
        return answer

    async def _update_memory_about_user(self, user_id: int) -> None:
        history = self.user_repository.get_history(user_id)
        current_memory = self.user_repository.get_memory(user_id)
        new_memory = await self.llm_client.get_answer(
            self.update_memory_prompt + "# History:\n" + history + "# Current memory:\n" + current_memory,
            temperature=0.5
        )
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
        prompt = self.check_prompt.format(
            message=user_message,
            topic_list=TOPIC_LIST,
            prev_mistake=prev_mistake
        )

        raw = await self.llm_client.get_answer(prompt, temperature=0.3)
        raw = raw.strip()

        if raw == "NO_ERROR" or not raw:
            return "", False

        if "|" not in raw:
            return raw, False

        mistake_text, error_type = raw.rsplit("|", 1)
        error_type = error_type.strip().upper()

        prev_type = EnglishTeacher._extract_type(prev_mistake)

        is_repeat = prev_type != "" and prev_type == error_type
        return raw, is_repeat

    @staticmethod
    def _extract_type(mistake_str: str) -> str:
        if not mistake_str or "|" not in mistake_str:
            return ""
        return mistake_str.rsplit("|", 1)[-1].strip().upper()
