import logging
import os

import httpx
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None:
        return

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                context.bot_data["api_url"],
                json={"message": update.message.text},
            )
            response.raise_for_status()
            answer = response.json()["answer"]
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        logger.exception("Could not get an answer from the API")
        await update.message.reply_text(
            "Не удалось получить ответ от сервиса. Попробуйте позже."
        )
        return

    await update.message.reply_text(str(answer))


def create_application() -> Application:
    token = os.getenv("TELEGRAM_TOKEN")
    api_url = os.getenv("API_URL")

    if not token:
        raise RuntimeError("TELEGRAM_TOKEN is not configured.")
    if not api_url:
        raise RuntimeError("API_URL is not configured.")

    application = Application.builder().token(token).build()
    application.bot_data["api_url"] = api_url
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    return application


def run() -> None:
    logging.basicConfig(level=logging.INFO)
    create_application().run_polling()
