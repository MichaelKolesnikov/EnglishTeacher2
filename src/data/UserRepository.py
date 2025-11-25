import psycopg2
from src.core.IUserRepository import IUserRepository
import json


class UserRepository(IUserRepository):
    def __init__(self, connection_string: str = None):
        if connection_string is None:
            connection_string = UserRepository._get_default_connection_string()
        self.connection_string = connection_string
        self._ensure_tables_exist()\

    def get_top_error_types(self, user_id: int, top_n: int = 3) -> list[str]:
        counters = self.get_error_counters_dict(user_id)
        if not counters:
            return []
        sorted_items = sorted(counters.items(), key=lambda x: x[1], reverse=True)
        return [error_type for error_type, count in sorted_items[:top_n]]

    def get_error_counter(self, user_id: int, error_type: str) -> int:
        counters = self.get_error_counters_dict(user_id)
        return counters.get(error_type, 0)

    def update_error_counter(self, user_id: int, error_type: str, value: int):
        counters = self.get_error_counters_dict(user_id)
        counters[error_type] = min(100, max(0, value))  # защита от багов
        self.save_error_counters_dict(user_id, counters)

    def get_error_counters_dict(self, user_id: int) -> dict[str, int]:
        """Возвращает весь словарь error_counters как dict[str, int]"""
        sql = "SELECT error_counters FROM users WHERE user_id = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user_id,))
                row = cursor.fetchone()
                if row and row[0]:
                    # Приводим все значения к int
                    raw = row[0]  # это dict из JSONB
                    return {k: int(v) if isinstance(v, (str, int)) else 0 for k, v in raw.items()}
        return {}

    def save_error_counters_dict(self, user_id: int, counters: dict[str, int]):
        """Сохраняет весь словарь обратно в БД"""
        sql = """
            UPDATE users 
            SET error_counters = %s::jsonb, 
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
        """
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (json.dumps(counters), user_id))
                conn.commit()

    def decrement_all_error_counters(self, user_id: int, excluded_type: str | None = None):
        """
        Уменьшает все счётчики на 1 (кроме excluded_type), но не ниже 0.
        Работает через Python — 100% надёжно.
        """
        counters = self.get_error_counters_dict(user_id)

        for error_type in counters:
            if error_type != excluded_type:
                counters[error_type] = max(0, counters[error_type] - 1)

        # Удаляем нулевые значения (по желанию — чище)
        counters = {k: v for k, v in counters.items() if v > 0}

        self.save_error_counters_dict(user_id, counters)

    def get_topic_status(self, user_id: int, topic_key: str) -> dict:
        with open("src/data/sql/get_topic_status.sql") as f:
            sql = f.read()
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (user_id, topic_key))
                row = cur.fetchone()
                if row:
                    return {
                        "status": row[0],
                        "mastery_streak": row[1],
                        "times_correct": row[2],
                        "times_mistake": row[3],
                    }
                return {
                    "status": "new",
                    "mastery_streak": 0,
                    "times_correct": 0,
                    "times_mistake": 0,
                }

    def upsert_topic_status(
            self,
            user_id: int,
            topic_key: str,
            status: str | None = None,
            mastery_streak: int | None = None,
            times_correct: int | None = None,
            times_mistake: int | None = None,
            last_mastered: bool | None = None,
            last_mistake: bool | None = None,
    ) -> None:
        with open("src/data/sql/upsert_topic_status.sql") as f:
            sql = f.read()

        params = (
            user_id, topic_key,
            status, mastery_streak,
            times_correct or 0, times_mistake or 0,
            last_mastered, last_mistake
        )

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                conn.commit()

    def get_mistake(self, user_id: int) -> str:
        if not self.user_exists(user_id):
            self.create_user(user_id, "A1")

        sql = "SELECT mistake FROM users WHERE user_id = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()
                return result[0] if result else ""

    def set_mistake(self, user_id: int, mistake: str) -> None:
        if not self.user_exists(user_id):
            self.create_user(user_id, "A1")

        sql = "UPDATE users SET mistake = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (mistake, user_id))
                conn.commit()

    @staticmethod
    def _get_default_connection_string() -> str:
        return "dbname='database' user='root' password='root' host='localhost' port='5432'"

    def _get_connection(self):
        return psycopg2.connect(self.connection_string)

    def _ensure_tables_exist(self) -> None:
        with open("src/data/sql/_ensure_tables_exist.sql") as f:
            create_tables_sql = f.read()

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_tables_sql)
                conn.commit()

    def add_new_message(self, user_id: int, message: str, participant: str) -> None:
        if not self.user_exists(user_id):
            self.create_user(user_id, "A1")

        sql = "INSERT INTO messages (user_id, message, participant) VALUES (%s, %s, %s)"
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user_id, message, participant))
                conn.commit()

    def get_correction_state(self, user_id: int) -> int:
        if not self.user_exists(user_id):
            return 0

        sql = "SELECT correction_state FROM users WHERE user_id = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()
                return result[0] if result else 0

    def set_correction_state(self, user_id: int, correction_state: int) -> None:
        if not self.user_exists(user_id):
            self.create_user(user_id, "A1")

        sql = "UPDATE users SET correction_state = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (correction_state, user_id))
                conn.commit()

    def get_history(self, user_id: int, limit: int = 20) -> str:
        if not self.user_exists(user_id):
            return ""

        with open("src/data/sql/get_history.sql") as f:
            sql = f.read()

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user_id, limit))
                messages = cursor.fetchall()
                history_lines = []
                for participant, message in reversed(messages):
                    prefix = "Student" if participant == str(user_id) else "Teacher"
                    history_lines.append(f"{prefix}: {message}")
                return "\n".join(history_lines)

    def get_memory(self, user_id: int) -> str:
        if not self.user_exists(user_id):
            return ""

        sql = "SELECT memory FROM users WHERE user_id = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()
                return result[0] if result else ""

    def set_memory(self, user_id: int, memory: str) -> None:
        if not self.user_exists(user_id):
            self.create_user(user_id, "A1")

        sql = "UPDATE users SET memory = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (memory, user_id))
                conn.commit()

    def user_exists(self, user_id: int) -> bool:
        sql = "SELECT 1 FROM users WHERE user_id = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user_id,))
                return cursor.fetchone() is not None

    def create_user(self, user_id: int, level: str) -> None:
        sql = "INSERT INTO users (user_id, level) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING"
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user_id, level))
                conn.commit()

    def get_user_level(self, user_id: int) -> str:
        if not self.user_exists(user_id):
            return "A1"

        sql = "SELECT level FROM users WHERE user_id = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()
                return result[0] if result else "A1"

    def set_user_level(self, user_id: int, level: str) -> None:
        if not self.user_exists(user_id):
            self.create_user(user_id, level)
            return

        sql = "UPDATE users SET level = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (level, user_id))
                conn.commit()
