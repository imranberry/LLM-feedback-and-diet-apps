"""Chatbot logic: streaming responses + persistent SQLite conversation history."""
import datetime
import sqlite3
from pathlib import Path
from typing import Generator, List, Optional

from langchain.chat_models import init_chat_model
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from . import config


class DietChatBot:
    def __init__(self, session_id: Optional[str] = None, model=None):
        """`model` can be injected (e.g. a fake model in tests)."""
        system_message = Path(config.PROMPT_PATH).read_text(encoding="utf-8")
        self.model = model or init_chat_model(
            config.MODEL_NAME,
            model_provider=config.MODEL_PROVIDER,
            temperature=0,
        )
        self.system_msg = SystemMessage(content=system_message)
        self._initialize_session(session_id)
        self._initialize_history()

    # ---- session handling -------------------------------------------------
    def _initialize_session(self, session_id: Optional[str] = None) -> None:
        self.session_id = session_id or self._generate_session_id()

    @staticmethod
    def _generate_session_id() -> str:
        return f"Diet Chat - {datetime.datetime.now():%Y-%m-%d %H:%M:%S}"

    def _initialize_history(self) -> None:
        self.history = SQLChatMessageHistory(
            session_id=self.session_id,
            connection=config.DB_CONNECTION_STRING,
        )
        if not self.history.get_messages():
            self.history.add_message(self.system_msg)

    def new_session(self) -> None:
        self._initialize_session()
        self._initialize_history()

    def load_session(self, session_id: str) -> None:
        if not session_id:
            return
        self._initialize_session(session_id)
        self._initialize_history()

    def get_messages(self) -> List[BaseMessage]:
        return self.history.get_messages()

    # ---- chat -------------------------------------------------------------
    def stream_response(self, user_message: str) -> Generator[str, None, None]:
        """Yield the AI reply chunk by chunk, saving both turns to history."""
        if not (user_message := user_message.strip()):
            return

        self.history.add_message(HumanMessage(content=user_message))

        response = ""
        for chunk in self.model.stream(self.history.get_messages()):
            if chunk.text:
                response += chunk.text
                yield chunk.text

        self.history.add_message(AIMessage(content=response))

    # ---- listing ----------------------------------------------------------
    @staticmethod
    def get_previous_conversations() -> List[str]:
        """Sessions that contain more than just the system message."""
        query = """
        SELECT session_id FROM message_store
        GROUP BY session_id
        HAVING COUNT(*) > 1
        ORDER BY session_id DESC
        """
        try:
            # `with sqlite3.connect()` only commits; it does not close, so close explicitly.
            conn = sqlite3.connect(config.DB_PATH)
            try:
                return [row[0] for row in conn.execute(query)]
            finally:
                conn.close()
        except sqlite3.OperationalError:
            # Table doesn't exist yet (first run, no chats saved).
            return []
