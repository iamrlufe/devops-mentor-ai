import logging
from urllib.parse import urlparse, urlunparse

import httpx
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.config import settings

REQUEST_TIMEOUT = 60.0
API_ERROR_MESSAGE = "Не удалось получить ответ от сервиса. Попробуйте позже."

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
        The parsed body, a body holding `error` when the API refused the
        request with a message worth showing, or `None` when it could not be
        reached at all.
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
            return {"error": error.response.json().get("detail", API_ERROR_MESSAGE)}
        except ValueError:
            return {"error": API_ERROR_MESSAGE}
    except (httpx.HTTPError, ValueError):
        logger.exception("Could not reach the API")

        return None


def chat_key(update: Update) -> str:
    """Return the workspace key of the chat an update belongs to."""
    return str(update.effective_chat.id)


async def reply(update: Update, text: str) -> None:
    """Answer the message that triggered the handler."""
    if update.message is not None:
        await update.message.reply_text(text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Answer a message in the workspace of the chat."""
    if update.message is None or update.message.text is None:
        return

    body = await call_api(
        context,
        "POST",
        "/chat",
        {"message": update.message.text, "chat_id": chat_key(update)},
    )

    if body is None:
        await reply(update, API_ERROR_MESSAGE)
        return

    await reply(update, str(body.get("error") or body.get("answer", API_ERROR_MESSAGE)))


async def list_agents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show every registered agent."""
    body = await call_api(context, "GET", "/agents")

    if body is None or "agents" not in body:
        await reply(update, API_ERROR_MESSAGE)
        return

    lines = [
        f"/agent {agent['name']} — {agent['description']}" for agent in body["agents"]
    ]

    await reply(update, "Доступные агенты:\n\n" + "\n".join(lines))


async def list_providers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show every registered provider and whether it works yet."""
    body = await call_api(context, "GET", "/providers")

    if body is None or "providers" not in body:
        await reply(update, API_ERROR_MESSAGE)
        return

    lines = [
        f"/provider {provider['name']} — "
        f"{'готов' if provider['implemented'] else 'не реализован'}"
        for provider in body["providers"]
    ]

    await reply(update, "Доступные провайдеры:\n\n" + "\n".join(lines))


async def switch_field(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    field: str,
    usage: str,
) -> None:
    """Change one field of the workspace of this chat."""
    if not context.args:
        await reply(update, f"Использование: {usage}")
        return

    body = await call_api(
        context,
        "POST",
        "/workspace",
        {"chat_id": chat_key(update), field: context.args[0]},
    )

    if body is None:
        await reply(update, API_ERROR_MESSAGE)
        return

    if "error" in body:
        await reply(update, str(body["error"]))
        return

    await reply(update, f"{field}: {body['workspace'][field]}")


async def switch_agent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Switch the agent of this chat."""
    await switch_field(update, context, "agent", "/agent docker")


async def switch_provider(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Switch the LLM provider of this chat."""
    await switch_field(update, context, "provider", "/provider groq")


async def show_workspace(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show what this chat currently runs on."""
    body = await call_api(context, "GET", f"/workspace/{chat_key(update)}")

    if body is None or "resolved" not in body:
        await reply(update, API_ERROR_MESSAGE)
        return

    resolved = body["resolved"]
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


def create_application() -> Application:
    """Build the bot with its command and message handlers.

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

    application.add_handler(CommandHandler("agents", list_agents))
    application.add_handler(CommandHandler("providers", list_providers))
    application.add_handler(CommandHandler("agent", switch_agent))
    application.add_handler(CommandHandler("provider", switch_provider))
    application.add_handler(CommandHandler("workspace", show_workspace))
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
