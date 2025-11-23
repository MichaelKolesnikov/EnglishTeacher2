import psycopg2
from src.core.IUserRepository import IUserRepository


class UserRepository(IUserRepository):
    def __init__(self, connection_string: str = None):
        if connection_string is None:
            connection_string = UserRepository._get_default_connection_string()
        self.connection_string = connection_string
        self._ensure_tables_exist()

    @staticmethod
    def _get_default_connection_string() -> str:
        return "dbname='database' user='root' password='root' host='localhost' port='5432'"

    def _get_connection(self):
        return psycopg2.connect(self.connection_string)

    def _ensure_tables_exist(self) -> None:
        create_tables_sql = """
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            level VARCHAR(20) DEFAULT 'A1',
            correction_state INTEGER DEFAULT 0,
            memory TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
            message TEXT NOT NULL,
            participant VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
        CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
        """

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

        sql = """
        SELECT participant, message 
        FROM messages 
        WHERE user_id = %s 
        ORDER BY created_at DESC 
        LIMIT %s
        """
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
