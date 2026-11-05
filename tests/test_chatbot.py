from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from diet_assistant.logic import DietChatBot


def make_bot(reply="Hello there friend", session_id=None):
    model = GenericFakeChatModel(messages=iter([AIMessage(content=reply)] * 5))
    return DietChatBot(session_id=session_id, model=model)


def test_no_conversations_on_fresh_db():
    assert DietChatBot.get_previous_conversations() == []


def test_streaming_yields_chunks_and_saves_history():
    bot = make_bot()
    chunks = list(bot.stream_response("I want to lose weight"))
    assert len(chunks) >= 1
    assert "".join(chunks) == "Hello there friend"

    msgs = bot.get_messages()
    assert [m.type for m in msgs] == ["system", "human", "ai"]
    assert msgs[-1].content == "Hello there friend"


def test_empty_message_is_ignored():
    bot = make_bot()
    assert list(bot.stream_response("   ")) == []
    assert len(bot.get_messages()) == 1  # system prompt only


def test_conversations_persist_and_reload():
    bot = make_bot(session_id="s1")
    list(bot.stream_response("hi"))
    assert DietChatBot.get_previous_conversations() == ["s1"]

    reloaded = make_bot(session_id="s1")
    assert len(reloaded.get_messages()) == 3


def test_new_session_starts_clean():
    bot = make_bot(session_id="old")
    list(bot.stream_response("hi"))
    bot.new_session()
    assert bot.session_id != "old"
    assert len(bot.get_messages()) == 1
