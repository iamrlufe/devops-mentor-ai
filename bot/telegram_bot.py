import logging
from collections.abc import Awaitable, Callable
from urllib.parse import urlparse, urlunparse

import httpx
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.config import settings
from app.users.manager import UserManager
from bot import keyboards, texts

REQUEST_TIMEOUT = 60.0

STATE_KEY = "onboarding"
STATE_NAME = "awaiting_name"
STATE_PHONE = "awaiting_phone"

logger = logging.getLogger(__name__)


def api_base_url(chat_url: str) -> str:
    """Return the API root of the configured chat endpoint.

    `API_URL` points at the chat endpoint and the other endpoints live next to
    it, so the root is derived instead of adding a setting per route.
    """
    parsed = urlparse(chat_url)
    path = parsed.path.rstrip("/").removesuffix("/chat")

    return urlunparse(parsed._replace(path=path, query="", fragment=""))


async def call_api(
    context: ContextTypes.DEFAULT_TYPE,
    method: str,
    path: str,
    payload: dict | None = None,
) -> dict | None:
    """Call the platform API.

    Returns:
        The parsed body, a body holding `error` when the API refused the request
        with a message worth showing, or `None` when it could not be reached.
    """
    url = f"{context.bot_data['api_base_url']}{path}"

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.request(method, url, json=payload)
            response.raise_for_status()

            return response.json()
    except httpx.HTTPStatusError as error:
        logger.warning("API answered %s for %s", error.response.status_code, path)

        try:
            return {"error": error.response.json().get("detail", texts.API_ERROR)}
        except ValueError:
            return {"error": texts.API_ERROR}
    except (httpx.HTTPError, ValueError):
        logger.exception("Could not reach the API")

        return None


async def reply(update: Update, text: str, **kwargs: object) -> None:
    """Answer the message that triggered the handler."""
    if update.message is not None:
        await update.message.reply_text(text, **kwargs)


def profile_of(update: Update):
    """Return the profile of the user, creating it on first contact."""
    return UserManager.ensure_telegram_user(update.effective_user.id)


def workspace_key(update: Update) -> str:
    """Return the workspace key of a user: their platform id, not the chat id."""
    profile, _ = profile_of(update)

    return profile.user_id


async def _workspace_document(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> dict | None:
    body = await call_api(context, "GET", f"/workspace/{workspace_key(update)}")

    return body if body and "resolved" in body else None


async def _set_workspace(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    **changes: str,
) -> dict | None:
    profile, _ = profile_of(update)
    payload = {"chat_id": profile.user_id, "user_id": profile.user_id, **changes}

    return await call_api(context, "POST", "/workspace", payload)


# --- first run ----------------------------------------------------------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greet the user and start the first-run questions when needed."""
    profile, _ = profile_of(update)

    if not profile.is_complete():
        context.user_data[STATE_KEY] = STATE_NAME
        await reply(update, texts.WELCOME, reply_markup=ReplyKeyboardRemove())
        return

    await _send_ready(update, context)


async def edit_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ask the first-run questions again."""
    context.user_data[STATE_KEY] = STATE_NAME
    await reply(update, texts.EDIT_PROFILE, reply_markup=ReplyKeyboardRemove())


async def _finish_onboarding(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Show what the user ended up with and open the main menu."""
    profile, _ = profile_of(update)
    document = await _workspace_document(update, context)
    resolved = document["resolved"] if document else {}

    await reply(
        update,
        texts.PROFILE_SUMMARY.format(
            name=profile.name,
            user_id=profile.user_id,
            agent=resolved.get("agent", "-"),
            provider=resolved.get("provider", "-"),
            workspace=profile.user_id,
        ),
        reply_markup=keyboards.main_menu(),
    )
    await _send_ready(update, context)


async def _send_ready(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    document = await _workspace_document(update, context)
    resolved = document["resolved"] if document else {}

    await reply(
        update,
        texts.READY.format(
            agent=resolved.get("agent", "-"),
            provider=resolved.get("provider", "-"),
        ),
        reply_markup=keyboards.main_menu(),
    )


async def receive_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Store a phone number shared through the contact button."""
    profile, _ = profile_of(update)

    if update.message and update.message.contact:
        UserManager.update(profile.user_id, phone=update.message.contact.phone_number)

    context.user_data[STATE_KEY] = None
    await reply(update, texts.PHONE_SAVED, reply_markup=keyboards.main_menu())
    await _finish_onboarding(update, context)


# --- information --------------------------------------------------------------


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the profile of the user together with the stack they run on."""
    profile, _ = profile_of(update)
    document = await _workspace_document(update, context)
    resolved = document["resolved"] if document else {}

    lines = [
        f"Имя: {profile.name or '-'}",
        f"User ID: {profile.user_id}",
        f"Telegram ID: {profile.telegram_id}",
        f"Agent: {resolved.get('agent', '-')}",
        f"Provider: {resolved.get('provider', '-')}",
        f"Workspace: {profile.user_id}",
        f"Language: {profile.language}",
        f"Timezone: {profile.timezone}",
    ]

    if profile.phone:
        lines.append(f"Телефон: {profile.phone}")

    lines.append(f"Дата регистрации: {profile.created_at:%Y-%m-%d %H:%M} UTC")

    await reply(update, "\n".join(lines))


async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the short identity of the user."""
    profile, _ = profile_of(update)

    await reply(
        update,
        f"{profile.name or 'Без имени'}\n"
        f"User ID: {profile.user_id}\n"
        f"Telegram ID: {profile.telegram_id}",
    )


async def show_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the state of the platform behind the bot."""
    health = await call_api(context, "GET", "/health")

    if not health or "components" not in health:
        await reply(update, texts.API_ERROR)
        return

    store = health["vector_store"]
    documents = store.get("documents", -1)

    await reply(
        update,
        "\n".join(
            [
                f"Версия: {health['version']}",
                f"Состояние: {health['status']}",
                f"LLM: {health['llm_provider']}",
                f"Embedding: {health['embedding_provider']}",
                f"Retriever: {health['retriever_provider']}",
                f"Memory: {health['memory_provider']}",
                f"RAG: {'включён' if documents > 0 else 'индекс пуст'}",
                f"Collection: {store['collection']}",
                f"Документов: {documents if documents >= 0 else 'неизвестно'}",
            ]
        ),
    )


async def show_version(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the version of the platform."""
    body = await call_api(context, "GET", "/")

    if not body or "version" not in body:
        await reply(update, texts.API_ERROR)
        return

    await reply(
        update,
        "\n".join(
            [
                body["name"],
                f"Version {body['version']}",
                f"Release Date: {body.get('release_date', '-')}",
                f"Git Tag: v{body['version']}",
            ]
        ),
    )


async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Explain what the project is."""
    await reply(update, texts.ABOUT, disable_web_page_preview=True)


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Explain how the platform works."""
    await reply(update, texts.HELP, reply_markup=keyboards.main_menu())


async def show_chat_hint(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tell the user they can simply write."""
    await reply(update, texts.CHAT_HINT)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Put the workspace back to the platform defaults."""
    body = await _set_workspace(
        update,
        context,
        agent="",
        provider="",
        embedding="",
        memory="",
        retriever="",
        collection="",
        prompt="",
    )

    if body is None:
        await reply(update, texts.API_ERROR)
        return

    await reply(update, texts.RESET_DONE, reply_markup=keyboards.main_menu())


# --- choosing an agent and a provider -----------------------------------------


async def list_agents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show every agent as a button, marking the one in use."""
    body = await call_api(context, "GET", "/agents")
    document = await _workspace_document(update, context)

    if body is None or "agents" not in body:
        await reply(update, texts.API_ERROR)
        return

    current = document["resolved"]["agent"] if document else ""
    await reply(
        update,
        texts.PICK_AGENT,
        reply_markup=keyboards.agent_choices(body["agents"], current),
    )


async def list_providers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show every provider as a button; the unfinished ones are marked."""
    body = await call_api(context, "GET", "/providers")
    document = await _workspace_document(update, context)

    if body is None or "providers" not in body:
        await reply(update, texts.API_ERROR)
        return

    current = document["resolved"]["provider"] if document else ""
    await reply(
        update,
        texts.PICK_PROVIDER,
        reply_markup=keyboards.provider_choices(body["providers"], current),
    )


async def show_workspace(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show what this user runs on."""
    document = await _workspace_document(update, context)

    if document is None:
        await reply(update, texts.API_ERROR)
        return

    resolved = document["resolved"]
    labels = (
        ("Agent", "agent"),
        ("Provider", "provider"),
        ("Embedding", "embedding"),
        ("Retriever", "retriever"),
        ("Memory", "memory"),
        ("Collection", "collection"),
    )

    await reply(
        update,
        "\n\n".join(f"{label}:\n{resolved[key]}" for label, key in labels),
    )


async def switch_field(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    field: str,
    usage: str,
) -> None:
    """Change one field of the workspace from a command argument."""
    if not context.args:
        await reply(update, f"Использование: {usage}")
        return

    body = await _set_workspace(update, context, **{field: context.args[0]})

    if body is None:
        await reply(update, texts.API_ERROR)
        return

    if "error" in body:
        await reply(update, str(body["error"]))
        return

    await reply(update, f"{field}: {body['workspace'][field]}")


async def switch_agent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Switch the agent from `/agent <name>`."""
    await switch_field(update, context, "agent", "/agent docker")


async def switch_provider(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Switch the provider from `/provider <name>`."""
    await switch_field(update, context, "provider", "/provider groq")


async def on_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Apply a choice made with an inline button."""
    query = update.callback_query
    await query.answer()

    prefix, _, value = query.data.partition(keyboards.CALLBACK_SEPARATOR)

    if prefix == keyboards.UNAVAILABLE_CALLBACK_PREFIX:
        await query.edit_message_text(
            texts.NOT_IMPLEMENTED_CHOICE.format(name=value)
        )
        return

    profile, _ = profile_of(update)
    body = await call_api(
        context,
        "POST",
        "/workspace",
        {"chat_id": profile.user_id, "user_id": profile.user_id, prefix: value},
    )

    if body is None:
        await query.edit_message_text(texts.API_ERROR)
        return

    if "error" in body:
        await query.edit_message_text(str(body["error"]))
        return

    await query.edit_message_text(f"{prefix}: {body['workspace'][prefix]}")


# --- conversation -------------------------------------------------------------

#: Menu button to handler. A dictionary instead of a chain of comparisons, so a
#: new button is one more entry.
MENU_ACTIONS: dict[str, Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable]] = {
    keyboards.BUTTON_CHAT: show_chat_hint,
    keyboards.BUTTON_PROFILE: show_profile,
    keyboards.BUTTON_AGENTS: list_agents,
    keyboards.BUTTON_PROVIDERS: list_providers,
    keyboards.BUTTON_WORKSPACE: show_workspace,
    keyboards.BUTTON_HELP: show_help,
    keyboards.BUTTON_ABOUT: show_about,
}


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route a text message: first run answers, menu buttons, or a question."""
    if update.message is None or update.message.text is None:
        return

    text = update.message.text.strip()
    profile, created = profile_of(update)

    if created and not profile.is_complete():
        context.user_data[STATE_KEY] = STATE_NAME
        await reply(update, texts.WELCOME, reply_markup=ReplyKeyboardRemove())
        return

    state = context.user_data.get(STATE_KEY)

    if state == STATE_NAME:
        UserManager.update(profile.user_id, name=text)
        context.user_data[STATE_KEY] = STATE_PHONE
        await reply(
            update,
            texts.ASK_PHONE.format(name=text),
            reply_markup=keyboards.phone_request(),
        )
        return

    if state == STATE_PHONE:
        context.user_data[STATE_KEY] = None
        await reply(update, texts.PHONE_SKIPPED, reply_markup=keyboards.main_menu())
        await _finish_onboarding(update, context)
        return

    action = MENU_ACTIONS.get(text)

    if action is not None:
        await action(update, context)
        return

    body = await call_api(
        context,
        "POST",
        "/chat",
        {"message": text, "chat_id": profile.user_id},
    )

    if body is None:
        await reply(update, texts.API_ERROR)
        return

    await reply(update, str(body.get("error") or body.get("answer", texts.API_ERROR)))


COMMANDS: dict[str, Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable]] = {
    "start": start,
    "help": show_help,
    "about": show_about,
    "version": show_version,
    "profile": show_profile,
    "editprofile": edit_profile,
    "status": show_status,
    "reset": reset,
    "whoami": whoami,
    "agents": list_agents,
    "providers": list_providers,
    "workspace": show_workspace,
    "agent": switch_agent,
    "provider": switch_provider,
}


def create_application() -> Application:
    """Build the bot with its command, callback and message handlers.

    Raises:
        RuntimeError: If the token or the API address is missing.
    """
    token = settings.telegram_token
    api_url = settings.api_url

    if not token:
        raise RuntimeError("TELEGRAM_TOKEN is not configured.")
    if not api_url:
        raise RuntimeError("API_URL is not configured.")

    application = Application.builder().token(token).build()
    application.bot_data["api_url"] = api_url
    application.bot_data["api_base_url"] = api_base_url(api_url)

    for command, handler in COMMANDS.items():
        application.add_handler(CommandHandler(command, handler))

    application.add_handler(CallbackQueryHandler(on_choice))
    application.add_handler(MessageHandler(filters.CONTACT, receive_contact))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    return application


def run() -> None:
    """Start long polling."""
    logging.basicConfig(level=logging.INFO)
    # httpx logs every request URL, and the Telegram token is part of that
    # URL, so INFO logging would print the token into the container logs.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    create_application().run_polling()
