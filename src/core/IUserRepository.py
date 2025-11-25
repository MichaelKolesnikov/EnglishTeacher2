from abc import ABC, abstractmethod


class IUserRepository(ABC):
    @abstractmethod
    def get_topic_status(self, user_id: int, topic_key: str) -> dict:
        pass

    @abstractmethod
    def upsert_topic_status(
            self,
            user_id: int,
            topic_key: str,
            status: str | None = None,
            mastery_streak: int | None = None,
            times_correct: int | None = None,
            times_mistake: int | None = None,
            last_mastered: bool | None = None,
            last_mistake: bool | None = None
    ) -> None:
        pass

    @abstractmethod
    def get_mistake(self, user_id: int) -> str:
        pass

    @abstractmethod
    def set_mistake(self, user_id: int, mistake: str) -> None:
        pass

    @abstractmethod
    def add_new_message(self, user_id: int, message: str, participant: str) -> None:
        pass

    @abstractmethod
    def get_correction_state(self, user_id: int) -> int:
        pass

    @abstractmethod
    def set_correction_state(self, user_id, state: int) -> None:
        pass

    @abstractmethod
    def get_history(self, user_id: int) -> str:
        pass

    @abstractmethod
    def get_memory(self, user_id: int) -> str:
        pass

    @abstractmethod
    def set_memory(self, user_id: int, memory: str) -> None:
        pass

    @abstractmethod
    def user_exists(self, user_id: int) -> bool:
        pass

    @abstractmethod
    def create_user(self, user_id: int, level: str) -> None:
        pass

    @abstractmethod
    def get_user_level(self, user_id: int) -> str:
        pass

    @abstractmethod
    def set_user_level(self, user_id: int, level: str) -> None:
        pass
