from src.core.topics.registry import TOPICS


class TopicMaster:
    MASTERY_THRESHOLD = 3

    def __init__(self, user_repository):
        self.repo = user_repository

    def register_usage(self, user_id: int, topic_key: str, correct: bool):
        if topic_key not in TOPICS:
            return

        current = self.repo.get_topic_status(user_id, topic_key)

        if correct:
            new_streak = current["mastery_streak"] + 1
            new_status = "mastered" if new_streak >= self.MASTERY_THRESHOLD else current["status"]
            self.repo.upsert_topic_status(
                user_id, topic_key,
                status=new_status if new_status != current["status"] else None,
                mastery_streak=new_streak,
                times_correct=1,
            )
        else:
            new_status = "weak" if current["status"] == "mastered" else current["status"]
            if new_status == "weak":
                new_status = "practicing"
            self.repo.upsert_topic_status(
                user_id, topic_key,
                status="practicing" if current["status"] == "new" else new_status,
                mastery_streak=0,
                times_mistake=1,
            )

    def get_next_topic(self, user_id: int, current_cefr: str) -> str | None:
        import random
        candidates = [
            key for key, info in TOPICS.items()
            if info["cefr"] <= current_cefr[:2]  # A1 <= A, B1 <= B и т.д.
        ]
        if not candidates:
            return None

        weights = []
        for key in candidates:
            status = self.repo.get_topic_status(user_id, key)["status"]
            if status == "new":
                weights.append(10)
            elif status == "weak":
                weights.append(8)
            elif status == "practicing":
                weights.append(4)
            else:  # mastered
                weights.append(1)

        return random.choices(candidates, weights=weights, k=1)[0]
