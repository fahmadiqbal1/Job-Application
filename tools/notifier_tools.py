"""Notification tools for Telegram and email."""

import asyncio
from typing import Optional

import aiosmtplib
from email.mime.text import MIMEText
from langchain.tools import tool
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

from config.settings import settings
from state.confirmation import (
    register_pending,
    resolve_confirmation,
    get_result,
    clear_confirmation,
)
from api.websocket import emit_confirmation_request

# Module-level shared Bot instance — initialized in main.py
_bot: Optional[Bot] = None


def set_bot(bot: Bot) -> None:
    """Set the Telegram bot instance (call from main.py at startup)."""
    global _bot
    _bot = bot


async def _send_with_retry(coro, max_retries: int = 3) -> None:
    """Send Telegram message with retry backoff."""
    backoff = [1, 2]
    for attempt in range(max_retries):
        try:
            return await coro
        except Exception as e:
            if attempt < len(backoff):
                await asyncio.sleep(backoff[attempt])
            elif attempt == max_retries - 1:
                raise


@tool("send_telegram_message", parse_docstring=True)
async def send_telegram_message(chat_id: str, text: str) -> str:
    """Send a Telegram message to the user.

    Args:
        chat_id: Telegram chat ID to send to.
        text: Message text (markdown supported).

    Returns:
        Confirmation string.
    """
    if not _bot:
        return "Error: Telegram bot not initialized"

    try:
        await _send_with_retry(
            _bot.send_message(chat_id=int(chat_id), text=text, parse_mode="Markdown")
        )
        return f"Message sent to {chat_id}"
    except Exception as e:
        return f"Error sending message: {str(e)}"


async def send_telegram_direct(chat_id: str, text: str) -> None:
    """Lightweight send — for orchestrator status updates (bypasses agent)."""
    if not _bot:
        return
    try:
        await _bot.send_message(chat_id=int(chat_id), text=text, parse_mode="Markdown")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")


@tool("request_telegram_confirmation", parse_docstring=True)
async def request_telegram_confirmation(
    chat_id: str,
    job_id: str,
    job_title: str,
    company: str,
    cover_letter_preview: str,
    ats_score: Optional[int] = None,
) -> str:
    """Send job application preview to Telegram and wait for YES/SKIP confirmation.

    Args:
        chat_id: Telegram chat ID.
        job_id: Unique job identifier.
        job_title: Job title.
        company: Company name.
        cover_letter_preview: First 400 characters of the cover letter.
        ats_score: Optional ATS score (0-100).

    Returns:
        "YES" or "SKIP" based on user response (or "SKIP" if timeout).
    """
    # Register pending confirmation using shared state module
    event = register_pending(job_id)

    # Broadcast to web frontend via WebSocket
    try:
        await emit_confirmation_request(
            job_id, job_title, company, cover_letter_preview, ats_score
        )
    except Exception as e:
        print(f"WebSocket emit failed: {e}")

    if not _bot or chat_id == "web":
        # Web-only mode or no Telegram configured
        try:
            await asyncio.wait_for(event.wait(), timeout=settings.confirmation_timeout_secs)
            return get_result(job_id)
        except asyncio.TimeoutError:
            return "SKIP"
        finally:
            clear_confirmation(job_id)

    # Send confirmation message with inline keyboard (Telegram)
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ YES — Apply", callback_data=f"YES:{job_id}"),
                InlineKeyboardButton("⏭ SKIP", callback_data=f"SKIP:{job_id}"),
            ]
        ]
    )

    try:
        score_text = f" [ATS: {ats_score}%]" if ats_score else ""
        await _bot.send_message(
            chat_id=int(chat_id),
            text=f"*{job_title}* at *{company}*{score_text}\n\n_{cover_letter_preview}_",
            reply_markup=keyboard,
            parse_mode="Markdown",
        )

        # Wait for response with timeout
        try:
            await asyncio.wait_for(event.wait(), timeout=settings.confirmation_timeout_secs)
            return get_result(job_id)
        except asyncio.TimeoutError:
            return "SKIP"

    finally:
        clear_confirmation(job_id)


@tool("send_email_confirmation", parse_docstring=True)
async def send_email_confirmation(
    recipient_email: str, subject: str, body: str
) -> str:
    """Send email confirmation via SMTP (Gmail).

    Args:
        recipient_email: Recipient email address.
        subject: Email subject.
        body: Email body text.

    Returns:
        Confirmation string or error message.
    """
    try:
        message = MIMEText(body)
        message["Subject"] = subject
        message["From"] = settings.smtp_user
        message["To"] = recipient_email

        async with aiosmtplib.SMTP(hostname=settings.smtp_host, port=settings.smtp_port) as smtp:
            await smtp.login(settings.smtp_user, settings.smtp_pass)
            await smtp.send_message(message)

        return f"Email sent to {recipient_email}"
    except Exception as e:
        return f"Error sending email: {str(e)}"
