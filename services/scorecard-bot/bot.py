"""
Telegram Scorecard Bot
Usage: /scorecard AAPL  or  /scorecard RELIANCE
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from scorecard_engine import run_scorecard

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ALPHA_VANTAGE_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "66TFRARVDRBLXEGS")

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

HELP_TEXT = """
📊 *Stock Scorecard Bot*

Instant 7-metric quality check for any stock — Indian or Global.

*Commands:*
• `/scorecard AAPL` — Global stock (US/NASDAQ)
• `/scorecard RELIANCE` — Indian stock (NSE)
• `/scorecard HDFCBANK` — Indian bank (D/E adjusted)
• `/help` — Show this message

*Metrics scored:*
1. P/E Ratio
2. ROIC (Return on Invested Capital)
3. D/E Ratio (Debt-to-Equity)
4. EPS CAGR (5yr & 3yr)
5. ROE (Return on Equity)
6. EBIT Margin
7. Gross Margin

_Results are for educational purposes only. Not investment advice._
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Welcome to *Stock Scorecard Bot*\\!\n\n"
        "Type `/scorecard AAPL` to get a 1\\-min quality scorecard for any stock\\.\n\n"
        "Use `/help` to see all commands\\.",
        parse_mode="MarkdownV2",
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")


async def scorecard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "⚠️ Please provide a ticker symbol.\n\nExample: `/scorecard AAPL`",
            parse_mode="Markdown",
        )
        return

    ticker = context.args[0].upper().strip()
    logger.info(f"Scorecard requested for: {ticker} by {update.effective_user.username}")

    # Send "typing" indicator
    await update.message.chat.send_action("typing")

    # Send a "loading" message first so user knows we're working
    loading_msg = await update.message.reply_text(
        f"⏳ Fetching live data for *{ticker}*...", parse_mode="Markdown"
    )

    try:
        result = await run_scorecard(ticker, ALPHA_VANTAGE_KEY)
        await loading_msg.edit_text(result, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error computing scorecard for {ticker}: {e}", exc_info=True)
        await loading_msg.edit_text(
            f"❌ Could not generate scorecard for *{ticker}*.\n\n"
            f"Possible causes:\n"
            f"• Invalid ticker symbol\n"
            f"• API rate limit hit (Alpha Vantage: 25 req/day on free tier)\n"
            f"• Network issue\n\n"
            f"Try again in a moment.",
            parse_mode="Markdown",
        )


def main() -> None:
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN environment variable not set!")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("scorecard", scorecard))

    logger.info("🤖 Scorecard Bot is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
