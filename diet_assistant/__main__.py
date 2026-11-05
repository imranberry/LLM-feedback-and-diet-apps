"""Run with:  python -m diet_assistant"""
from .logic import DietChatBot
from .ui import PersistentChatBotUI


def main() -> None:
    ui = PersistentChatBotUI(DietChatBot())
    ui.create_ui().launch()


if __name__ == "__main__":
    main()
