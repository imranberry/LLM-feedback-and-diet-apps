from diet_assistant.ui import PersistentChatBotUI


class StubBot:
    session_id = "x"

    def stream_response(self, msg):
        yield from ["Eat ", "more ", "veg"]

    def get_previous_conversations(self):
        return []


def test_stream_handler_builds_up_reply():
    ui = PersistentChatBotUI(StubBot())
    states = list(ui.stream_message_handler("help", []))
    assert states[-1][1][-1].content == "Eat more veg"
    assert states[-1][1][0].role == "user"


def test_interface_builds():
    PersistentChatBotUI(StubBot()).create_ui()
