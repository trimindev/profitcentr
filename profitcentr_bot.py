from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    Application,
)
from asyncio import run
import requests


async def auto_command(update, context):
    pa = context.bot_data["pa"]
    await pa.auto()
    await update.message.reply_text("play")


async def start_command(update, context):
    pa = context.bot_data["pa"]
    app = context.bot_data["app"]
    await pa.start()


async def stop_command(update, context):
    await update.message.reply_text("Stopping...")
    await context.bot.stop_running()
    await update.message.reply_text("Bot stopped.")


async def enter_text(update, context):
    entered_text = update.message.text
    await update.message.reply_text(f"You entered: {entered_text}")

    # End the conversation
    return ConversationHandler.END


async def login_command(update, context):
    await update.message.reply_text("Please enter something:")

    return ENTER_TEXT_STATE


default_token = "6515288738:AAExXIQALfgSvUSFYFP2g1EE3qLZwntLKYQ"
default_chat_id = "6302326801"
ENTER_TEXT_STATE = 1


class Bot:
    def __init__(self, token=default_token, chat_id=default_chat_id) -> None:
        self.token = token
        self.chat_id = chat_id

        self.app = Application.builder().token(token).build()

        self.bot = self.app.bot
        self.app.bot_data["bot"] = self.bot

        self.app.add_handler(
            ConversationHandler(
                entry_points=[CommandHandler("login", login_command)],
                states={
                    ENTER_TEXT_STATE: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, enter_text)
                    ],
                },
                fallbacks=[],
            )
        )

    def run(self):
        print("Starting Profitcentr bot....")
        self.send_message("Starting Profitcentr bot...")
        self.app.run_polling()

    def send_message(self, text):
        self.bot.sendMessage(chat_id=self.chat_id, text=text)

    def get_chat_id(self):
        url = f"https://api.telegram.org/bot{self.token}/getUpdates"
        response = requests.get(url)
        data = response.json()
        chat_id = data["result"][0]["message"]["chat"]["id"]
        print(chat_id)


bot = Bot()

bot.run()
