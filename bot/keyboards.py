"""Keyboards of the Telegram bot."""

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

BUTTON_CHAT = "💬 Чат"
BUTTON_PROFILE = "👤 Профиль"
BUTTON_AGENTS = "🤖 Агенты"
BUTTON_PROVIDERS = "🧠 Провайдеры"
BUTTON_WORKSPACE = "⚙ Workspace"
BUTTON_HELP = "📚 Помощь"
BUTTON_ABOUT = "ℹ О проекте"

BUTTON_SHARE_PHONE = "📱 Отправить номер"
BUTTON_SKIP_PHONE = "Пропустить"

AGENT_CALLBACK_PREFIX = "agent"
PROVIDER_CALLBACK_PREFIX = "provider"
UNAVAILABLE_CALLBACK_PREFIX = "unavailable"
CALLBACK_SEPARATOR = ":"

MENU_LAYOUT = (
    (BUTTON_CHAT, BUTTON_PROFILE),
    (BUTTON_AGENTS, BUTTON_PROVIDERS),
    (BUTTON_WORKSPACE, BUTTON_HELP),
    (BUTTON_ABOUT,),
)

BUTTONS_PER_ROW = 2


def main_menu() -> ReplyKeyboardMarkup:
    """Return the persistent main menu."""
    return ReplyKeyboardMarkup(
        [list(row) for row in MENU_LAYOUT],
        resize_keyboard=True,
    )


def phone_request() -> ReplyKeyboardMarkup:
    """Return the keyboard that offers to share a phone number or skip it."""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BUTTON_SHARE_PHONE, request_contact=True)],
            [KeyboardButton(BUTTON_SKIP_PHONE)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def _rows(buttons: list[InlineKeyboardButton]) -> list[list[InlineKeyboardButton]]:
    return [
        buttons[index : index + BUTTONS_PER_ROW]
        for index in range(0, len(buttons), BUTTONS_PER_ROW)
    ]


def agent_choices(agents: list[dict], current: str) -> InlineKeyboardMarkup:
    """Return a button per agent, marking the one in use."""
    buttons = [
        InlineKeyboardButton(
            f"✅ {agent['name']}" if agent["name"] == current else agent["name"],
            callback_data=(
                f"{AGENT_CALLBACK_PREFIX}{CALLBACK_SEPARATOR}{agent['name']}"
            ),
        )
        for agent in agents
    ]

    return InlineKeyboardMarkup(_rows(buttons))


def provider_choices(providers: list[dict], current: str) -> InlineKeyboardMarkup:
    """Return a button per provider.

    A provider that is registered but not implemented is shown as coming soon
    and carries a callback that only explains itself, so it cannot be selected.
    """
    buttons = []

    for provider in providers:
        name = provider["name"]

        if not provider["implemented"]:
            buttons.append(
                InlineKeyboardButton(
                    f"🔒 {name} — Coming Soon",
                    callback_data=(
                        f"{UNAVAILABLE_CALLBACK_PREFIX}{CALLBACK_SEPARATOR}{name}"
                    ),
                )
            )
            continue

        buttons.append(
            InlineKeyboardButton(
                f"✅ {name}" if name == current else name,
                callback_data=(
                    f"{PROVIDER_CALLBACK_PREFIX}{CALLBACK_SEPARATOR}{name}"
                ),
            )
        )

    return InlineKeyboardMarkup(_rows(buttons))
