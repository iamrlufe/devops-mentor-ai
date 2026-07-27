"""Telegram administration: a thin client over the Admin API.

Every command here does one thing — call `/api/v1/admin/*` and format the
answer. There is no SQL, no counting and no permission rule in this module: the
platform decides all of it, so a web dashboard or a CLI written tomorrow behaves
exactly the same.
"""

import logging

import httpx
from telegram import Update
from telegram.ext import ContextTypes

from app.config import settings
from bot import texts

API_V1_PREFIX = "/api/v1"
ADMIN_PATH = "/admin"
REQUEST_TIMEOUT = 30.0
FORBIDDEN = 403
PREVIEW_ROWS = 10

logger = logging.getLogger(__name__)


def admin_root(api_base_url: str) -> str:
    """Return the root of the Admin API.

    The administration is served under the versioned prefix only, while
    `API_URL` may point at either the versioned or the original chat path, so
    the prefix is added when it is not already there.
    """
    base = api_base_url.rstrip("/")

    if base.endswith(API_V1_PREFIX):
        return f"{base}{ADMIN_PATH}"

    return f"{base}{API_V1_PREFIX}{ADMIN_PATH}"


async def call_admin_api(
    context: ContextTypes.DEFAULT_TYPE,
    update: Update,
    path: str,
) -> dict | None:
    """Call the Admin API as the Telegram user making the request.

    The Telegram id travels in a header and the platform decides whether it
    belongs to an administrator.

    Returns:
        The parsed body, `{"denied": True}` when the platform refused, or
        `None` when it could not be reached.
    """
    url = f"{admin_root(context.bot_data['api_base_url'])}{path}"
    headers = {"X-Telegram-Id": str(update.effective_user.id)}

    if settings.admin_api_key:
        headers["X-Admin-Key"] = settings.admin_api_key

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(url, headers=headers)

            if response.status_code == FORBIDDEN:
                return {"denied": True}

            response.raise_for_status()

            return response.json()
    except (httpx.HTTPError, ValueError):
        logger.exception("Could not reach the Admin API")

        return None


async def _answer(update: Update, body: dict | None, lines: list[str]) -> None:
    """Send the formatted answer, or explain why there is none."""
    if body is None:
        await update.message.reply_text(texts.API_ERROR)
        return

    if body.get("denied"):
        await update.message.reply_text(texts.ADMIN_DENIED)
        return

    await update.message.reply_text("\n".join(lines))


async def admin_home(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show what an administrator can do."""
    body = await call_admin_api(context, update, "")
    lines = []

    if body and not body.get("denied"):
        lines = [f"Роль: {body['identity']['role']}", "", texts.ADMIN_HELP]

    await _answer(update, body, lines)


async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the platform summary."""
    body = await call_admin_api(context, update, "/dashboard")
    lines = []

    if body and not body.get("denied"):
        lines = [
            f"Версия: {body['version']}",
            f"Аптайм: {body['uptime']} с",
            "",
            f"Пользователей: {body['users_total']}",
            f"Активны сегодня: {body['active_today']}",
            f"Активны за неделю: {body['active_week']}",
            "",
            f"Сообщений: {body['messages_total']} (сегодня {body['messages_today']})",
            f"Диалогов: {body['conversations_total']}",
            f"Workspace: {body['workspaces_total']}",
            f"Организаций: {body['organizations_total']}",
            "",
            f"Документов: {body['documents_total']}",
            f"Коллекций: {body['collections_total']}",
            "",
            f"Агентов: {body['agents_total']}",
            f"Провайдеров: {body['providers_total']}",
            f"Embedding: {body['embedding_providers_total']}",
            f"Memory: {body['memory_providers_total']}",
            f"Retriever: {body['retrievers_total']}",
        ]

    await _answer(update, body, lines)


async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the platform statistics."""
    body = await call_admin_api(context, update, "/statistics")
    lines = []

    if body and not body.get("denied"):
        users = body["users"]
        lines = [
            f"Пользователей: {users['total']}",
            f"Активны сегодня: {users['active_today']}",
            f"Активны за неделю: {users['active_week']}",
            f"Регистраций сегодня: {users['registered_today']}",
            f"Среднее время ответа: {body['average_response_time']} мс",
            "",
            "Агенты:",
        ]
        lines += [
            f"  {row['name']}: {row['requests']}"
            for row in body["agents_usage"][:PREVIEW_ROWS]
        ] or ["  нет данных"]
        lines += ["", "Провайдеры:"]
        lines += [
            f"  {row['name']}: {row['requests']}"
            for row in body["providers_usage"][:PREVIEW_ROWS]
        ] or ["  нет данных"]
        lines += ["", f"Организаций: {len(body['organizations'])}"]
        lines += [f"Workspace: {body['workspaces']['total']}"]

    await _answer(update, body, lines)


async def users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the newest users."""
    body = await call_admin_api(context, update, f"/users?limit={PREVIEW_ROWS}")
    lines = []

    if body and not body.get("denied"):
        lines = [f"Пользователей показано: {body['count']}", ""]
        lines += [
            f"{row['name'] or 'без имени'} — {row['user_id']}\n"
            f"  сообщений: {row['message_count']}, агент: {row['last_agent'] or '-'}, "
            f"провайдер: {row['last_provider'] or '-'}"
            for row in body["users"]
        ] or ["нет пользователей"]

    await _answer(update, body, lines)


async def agents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the agents and how much they are used."""
    body = await call_admin_api(context, update, "/agents")
    lines = []

    if body and not body.get("denied"):
        lines = [f"Агентов: {body['count']}", ""]
        lines += [
            f"{row['agent']}: сообщений {row['messages']}, "
            f"пользователей {row['users']}"
            for row in body["agents"]
        ]

    await _answer(update, body, lines)


async def providers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the providers with their errors and latency."""
    body = await call_admin_api(context, update, "/providers")
    lines = []

    if body and not body.get("denied"):
        lines = [f"Провайдеров: {body['count']}", ""]
        lines += [
            f"{row['provider']} — "
            f"{'готов' if row['implemented'] else 'не реализован'}\n"
            f"  запросов: {row['requests']}, ошибок: {row['errors']}, "
            f"средняя задержка: {row['average_latency']} мс"
            for row in body["providers"]
        ]

    await _answer(update, body, lines)


async def workspaces(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the stored workspaces."""
    body = await call_admin_api(context, update, f"/workspaces?limit={PREVIEW_ROWS}")
    lines = []

    if body and not body.get("denied"):
        lines = [f"Workspace: {body['count']}", ""]
        lines += [
            f"{row['chat_id']}: агент {row['agent'] or 'по умолчанию'}, "
            f"провайдер {row['provider'] or 'по умолчанию'}"
            for row in body["workspaces"]
        ] or ["нет рабочих областей"]

    await _answer(update, body, lines)


async def history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the newest messages of a user."""
    if not context.args:
        await update.message.reply_text("Использование: /history usr_xxxxxxxx")
        return

    user_id = context.args[0]
    body = await call_admin_api(
        context, update, f"/users/{user_id}/history?limit={PREVIEW_ROWS}"
    )
    lines = []

    if body and not body.get("denied"):
        lines = [f"История {user_id}: {body['count']} сообщений", ""]
        lines += [
            f"[{row['role']}] {row['message'][:120]}" for row in body["messages"]
        ] or ["история пуста"]

    await _answer(update, body, lines)


ADMIN_COMMANDS = {
    "admin": admin_home,
    "dashboard": dashboard,
    "stats": statistics,
    "users": users,
    "agents": agents,
    "providers": providers,
    "workspaces": workspaces,
    "history": history,
}
