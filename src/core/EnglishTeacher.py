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
        self.error_correction_prompts = {
            0: "The student made no grammar or vocabulary mistake in the last message. Just continue naturally.",
            1: "The student made a mistake of type {error_type}: \"{mistake}\". "
               "Gently hint at the correct form in your reply. Reply only in English.",
            2: "The student made a mistake of type {error_type}: \"{mistake}\". "
               "Clearly but kindly explain the mistake in English (1–2 sentences), then continue the conversation.",
            3: "The student repeated a mistake of type {error_type}: \"{mistake}\". "
               "Briefly explain the rule in Russian (1–2 short sentences, very friendly tone), "
               "then immediately switch back to English and continue warmly."
        }
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

    async def _get_correction_level_and_update_counters(
        self, user_id: int, error_type: str | None
    ) -> tuple[int, str]:
        if not error_type:
            self.user_repository.decrement_all_error_counters(user_id)
            return 0, self.error_correction_prompts[0]

        counter = self.user_repository.get_error_counter(user_id, error_type)

        if counter < 50:
            new_counter = min(100, counter + 30)
            level = 1
        elif counter < 80:
            new_counter = min(100, counter + 20)
            level = 2
        else:
            new_counter = 100
            level = 3

        self.user_repository.update_error_counter(user_id, error_type, new_counter)
        self.user_repository.decrement_all_error_counters(user_id, excluded_type=error_type)

        return level, self.error_correction_prompts[level]

    async def get_answer(self, user_id: int, user_message: str) -> str:
        self.user_repository.add_new_message(user_id, user_message, str(user_id))

        top_error_types = self.user_repository.get_top_error_types(user_id, top_n=3)
        top_errors_str = ", ".join(top_error_types) if top_error_types else "none"

        await self._update_memory_about_user(user_id)
        new_level = await self._update_level(user_id)

        mistake_raw = await self._get_mistake(
            user_message, top_errors_str
        )

        mistake_text = ""
        error_type = None

        if mistake_raw:
            parts = mistake_raw.split("||")
            mistake_text = parts[0].strip()
            if len(parts) >= 2:
                possible_topic = parts[1].strip()
                if possible_topic in TOPICS:
                    self.topic_master.register_usage(user_id, possible_topic, correct=False)
            if " | " in mistake_raw:
                error_part = mistake_raw.split("|", 1)[1].strip().split("||")[0].strip()
                error_type = error_part.upper()

        correction_level, correction_prompt = await self._get_correction_level_and_update_counters(
            user_id, error_type
        )

        self.user_repository.set_mistake(user_id, mistake_text or "")

        if not mistake_text and user_id not in self.message_counter:
            self.message_counter[user_id] = 0
        if not mistake_text:
            self.message_counter[user_id] = self.message_counter.get(user_id, 0) + 1
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
        prompt += correction_prompt.format(
            mistake=mistake_text or "",
            error_type=error_type or ""
        ) + self.prompt_divider

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
            self.update_memory_prompt.format(history=history, current_memory=current_memory),
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

    async def _get_mistake(self, user_message: str, top_error_types: str) -> str:
        prompt = self.check_prompt.format(
            message=user_message,
            topic_list=TOPIC_LIST,
            top_error_types=top_error_types
        )
        raw = await self.llm_client.get_answer(prompt, temperature=0.3)
        raw = raw.strip()

        if raw == "NO_ERROR":
            return ""
        return raw

    @staticmethod
    def _extract_type(mistake_str: str) -> str:
        if not mistake_str or "|" not in mistake_str:
            return ""
        return mistake_str.rsplit("|", 1)[-1].strip().upper()
