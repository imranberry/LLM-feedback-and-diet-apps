"""Gradio UI with streaming chat and a previous-conversations dropdown."""
from typing import Any, Generator, List, Tuple

import gradio as gr
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


class PersistentChatBotUI:
    def __init__(self, diet_chatbot):
        self.diet_chatbot = diet_chatbot

    def stream_message_handler(
        self, user_message: str, history: list
    ) -> Generator[Tuple[str, list], None, None]:
        if not (user_message := user_message.strip()):
            yield "", history
            return

        history.append(gr.ChatMessage(content=user_message, role="user"))
        history.append(gr.ChatMessage(content="", role="assistant"))
        yield "", history

        full_response = ""
        for chunk in self.diet_chatbot.stream_response(user_message):
            full_response += chunk
            history[-1] = gr.ChatMessage(content=full_response, role="assistant")
            yield "", history

    def new_session_handler(self) -> Tuple[list, Any]:
        self.diet_chatbot.new_session()
        return [], self.update_session_choices()

    def load_session_handler(self, session_id: str) -> Tuple[list, Any]:
        if not session_id:
            return [], self.update_session_choices()
        self.diet_chatbot.load_session(session_id)
        return (
            self._format_messages_for_ui(self.diet_chatbot.get_messages()),
            self.update_session_choices(),
        )

    @staticmethod
    def _format_messages_for_ui(messages: List[BaseMessage]) -> list:
        ui_messages = []
        for msg in messages[1:]:  # skip the system message
            if isinstance(msg, HumanMessage):
                ui_messages.append(gr.ChatMessage(content=msg.text, role="user"))
            elif isinstance(msg, AIMessage):
                ui_messages.append(gr.ChatMessage(content=msg.text, role="assistant"))
        return ui_messages

    def _session_choices(self) -> List[str]:
        """Saved sessions, always including the current (possibly still empty) one."""
        choices = list(self.diet_chatbot.get_previous_conversations())
        if self.diet_chatbot.session_id not in choices:
            choices.insert(0, self.diet_chatbot.session_id)
        return choices

    def update_session_choices(self) -> gr.update:
        return gr.update(choices=self._session_choices(), value=self.diet_chatbot.session_id)

    def create_ui(self) -> gr.Blocks:
        with gr.Blocks(title="Diet Planning Assistant") as interface:
            gr.Markdown("# Diet Planning Assistant")
            gr.Markdown("I can help you create balanced meal plans. Your conversations are saved!")

            chatbot = gr.Chatbot(max_height=400)

            with gr.Row():
                with gr.Column(scale=3):
                    msg = gr.Textbox(
                        placeholder="Ask about nutrition or diet plans...",
                        show_label=False,
                    )
                with gr.Column(scale=1):
                    submit = gr.Button("💬 Send", variant="primary")

            with gr.Row():
                sessions = gr.Dropdown(
                    choices=self._session_choices(),
                    value=self.diet_chatbot.session_id,
                    label="Previous Conversations",
                    interactive=True,
                )
                new = gr.Button("🆕 New Chat", size="sm")

            submit.click(self.stream_message_handler, [msg, chatbot], [msg, chatbot])
            msg.submit(self.stream_message_handler, [msg, chatbot], [msg, chatbot])
            new.click(self.new_session_handler, None, [chatbot, sessions])
            sessions.change(self.load_session_handler, sessions, [chatbot, sessions])
            interface.load(self.update_session_choices, None, sessions)

        return interface
