from asyncio import sleep
from profiles_handler import Profiles, default_profiles_options
from translate import Translator
import asyncio
import sys
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    Application,
)
import requests

sys.stdout.reconfigure(encoding="utf-8")


def get_chat_id(token):
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    response = requests.get(url)
    data = response.json()
    chat_id = data["result"][0]["message"]["chat"]["id"]
    print(chat_id)


def translate_text(text, source_language, target_language):
    translator = Translator(to_lang=target_language, from_lang=source_language)
    translation = translator.translate(text)
    return translation


class ProfitcentrAuto:
    default_profitcentr_options = {
        "url": "https://profitcentr.com/",
        "telegram_token": "6515288738:AAExXIQALfgSvUSFYFP2g1EE3qLZwntLKYQ",
        "profiles_options": default_profiles_options,
    }

    default_info = {
        "username": "ngmitr2512@gmail.com",
        "password": "fn7n6yr",
        "cookie": "",
        "profile_id": "98043",
    }

    def __init__(self, options=default_profitcentr_options) -> None:
        self.url = options.get("url")
        self.profiles_options = options.get("profiles_options")

        telegram_token = options.get("telegram_token")
        self.app = Application.builder().token(telegram_token).build()

        self.app.add_handler(
            ConversationHandler(
                entry_points=[CommandHandler("login", self.login_typing_command)],
                states={
                    1: [
                        MessageHandler(
                            filters.TEXT & ~filters.COMMAND, self.login_submit_command
                        )
                    ],
                },
                fallbacks=[],
            )
        )

        self.app.add_handler(CommandHandler("start", self.start_command))

    async def setAccountInfo(self, info=default_info):
        self.username = info.get("username")
        self.password = info.get("password")
        self.cookie = info.get("cookie")
        self.profile_id = info.get("profile_id")

    def runBot(self):
        print("Starting Profitcentr bot....")
        self.app.run_polling()

    async def start(self):
        p = Profiles(self.profiles_options)
        p.setProfileId(self.profile_id)

        browser = await p.start()
        page = await browser.newPage()
        await page.goto(self.url)

        self.page = page
        return browser

    async def add_cookie(self):
        await self.page.setCookie(self.cookie)

    async def get_captcha_title(self):
        captcha_title = await self.get_element_content(".out-capcha-title")
        translated_captcha_title = translate_text(captcha_title, "ru", "vi")

        return translated_captcha_title

    async def login_typing(self):
        login_button = await self.page.waitForSelector('a[href="/login"]', timeout=2000)

        await login_button.click()

        await self.page.waitForNavigation()

        username_input = await self.page.waitForSelector(
            "#login-form input[name='username']", timeout=2000
        )
        password_input = await self.page.waitForSelector(
            "#login-form input[name='password']", timeout=2000
        )
        await username_input.type(self.username)
        await password_input.type(self.password)

    async def login_submit(self):
        submit_button = await self.page.waitForSelector("#login-form button")
        await submit_button.click()

    async def get_element_content(self, selector):
        await self.page.waitForSelector(selector)

        element_content = await self.page.evaluate(
            f'document.querySelector("{selector}").textContent'
        )

        return element_content.strip()

    async def go_to_youtube_tab(self):
        title_menu = await self.page.waitForSelector("#mnu_title1.usermnutitle-g")
        menu_tab = await self.page.waitForSelector("#mnu_tblock1.usermnublock")
        youtube_button = await self.page.waitForSelector("#mnu_title1.usermnutitle-g")

        await title_menu.click()
        await menu_tab.click()
        await youtube_button.click()

    async def login_typing_command(self, update, context):
        await self.start()

        await self.login_typing()

        captcha_title = await self.get_captcha_title()

        await update.message.reply_text(captcha_title)

        return 1

    async def login_submit_command(self, update, context):
        number = int(update.message.text)

        await update.message.reply_text(number)

    async def start_command(self, update, context):
        await self.start()

    async def stop_command(update, context):
        await update.message.reply_text("Stopping...")
        await context.bot.stop_running()
        await update.message.reply_text("Stopped.")


async def main():
    await pa.setAccountInfo()


if __name__ == "__main__":
    pa = ProfitcentrAuto()

    # Run the asynchronous script
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    pa.runBot()
