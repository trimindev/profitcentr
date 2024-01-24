import html
import json
import logging
import traceback

from asyncio import sleep
from profiles_handler import Profiles, default_profiles_options
from translate import Translator
import asyncio
import sys
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    Application,
    ContextTypes,
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


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    # set higher logging level for httpx to avoid all GET and POST requests being logged
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)

    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=update.message.chat_id, text=message, parse_mode=ParseMode.HTML
    )


class ProfitcentrAuto:
    default_profitcentr_options = {
        "telegram_token": "6515288738:AAExXIQALfgSvUSFYFP2g1EE3qLZwntLKYQ",
        "profiles_options": default_profiles_options,
    }

    default_info = {
        "username": "ngmitr2512@gmail.com",
        "password": "fn7n6yr",
        "cookie": "",
        "profile_id": "96837",
    }

    STAGE_1, STAGE_2, STAGE_3 = range(3)

    def __init__(self, options=default_profitcentr_options) -> None:
        self.url = "https://profitcentr.com"
        self.profiles_options = options.get("profiles_options")

        telegram_token = options.get("telegram_token")
        self.app = Application.builder().token(telegram_token).build()

        self.p = Profiles(self.profiles_options)
        self.app.add_error_handler(error_handler)

        self.app.add_handler(
            ConversationHandler(
                entry_points=[CommandHandler("play", self.play_command)],
                states={
                    self.STAGE_1: [
                        MessageHandler(
                            filters.TEXT & ~filters.COMMAND,
                            self.play_state_1_command,
                        )
                    ],
                    self.STAGE_2: [
                        MessageHandler(
                            filters.TEXT & ~filters.COMMAND, self.play_state_2_command
                        )
                    ],
                },
                fallbacks=[],
            )
        )

    # ------------------------------------------------------------------
    # FUNCTIONS
    # ------------------------------------------------------------------
    async def setAccountInfo(self, info=default_info):
        self.username = info.get("username")
        self.password = info.get("password")
        self.cookie = info.get("cookie")
        self.profile_id = info.get("profile_id")

    def runBot(self):
        print("Starting Profitcentr bot....")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

    async def start(self):
        await self.p.setProfileId(self.profile_id)

        browser = await self.p.start()
        page = await browser.newPage()
        await page.goto(self.url)

        self.page = page
        return browser

    async def add_cookie(self):
        await self.page.setCookie(self.cookie)

    async def login_typing(self):
        login_button = await self.page.waitForSelector('a[href="/login"]')

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

    async def check_have_captcha(self):
        await sleep(3)
        captcha_title_element = await self.page.querySelector(".out-capcha-title")
        return captcha_title_element

    async def get_captcha_title(self):
        captcha_title_content = await self.page.evaluate(
            f'document.querySelector(".out-capcha-title").textContent'
        )
        translated_captcha_title = translate_text(captcha_title_content, "ru", "vi")
        return translated_captcha_title

    async def send_captcha_to_bot(self, update: Update):
        captcha_title = await self.get_captcha_title()

        # Take a screenshot
        screenshot_path = "screenshot.png"
        await self.page.screenshot({"path": screenshot_path})

        # Send the screenshot to the Telegram bot
        await self.app.bot.send_photo(
            update.message.chat_id, open(screenshot_path, "rb"), captcha_title
        )

    async def solve_captcha(self, update):
        number_list = list(map(int, update.message.text.split()))

        await self.page.waitForSelector(".out-capcha")

        for number in number_list:
            label_selector = f"label.out-capcha-lab:nth-child({number + 1})"
            label = await self.page.querySelector(label_selector)
            await label.click()

    async def resend_captcha_to_bot(self, update):
        await sleep(3)
        is_error = await self.page.querySelector(".msg-error")
        if is_error:
            await update.message.reply_text("Login fail, try again...")
            captcha_title = await self.get_captcha_title()
            await self.send_captcha_to_bot(captcha_title, update)

        return

    async def click_login_button(self):
        initial_url = self.page.url
        submit_button = await self.page.waitForSelector("#login-form button")
        await submit_button.click()

        await self.page.waitForNavigation({"waitUntil": "networkidle0"})

        return self.page.url == initial_url

    async def click_submit_captcha(self):
        submit_button = await self.page.waitForSelector(".btn.green")
        await submit_button.click()

        await sleep(3)
        is_error = await self.page.querySelector(".msg-error")

        return is_error

    async def go_to_youtube_tab(self):
        await self.page.waitForSelector("#mnu_tblock1")
        is_display_none = await self.page.evaluate(
            'window.getComputedStyle(document.getElementById("mnu_tblock1")).display === "none"'
        )

        if is_display_none:
            title_menu = await self.page.waitForSelector("#mnu_title1")
            await title_menu.click()

        elements = await self.page.querySelectorAll(
            "#mnu_tblock1 .ajax-site.user_menuline"
        )

        await elements[5].click()

    async def play_youtube(self):
        elements = await self.page.querySelectorAll(".work-youtube .work-serf span")
        print(elements)
        if elements:
            elements[1].click()
        else:
            print("not find elements")

    # ------------------------------------------------------------
    # COMMANDS
    # ------------------------------------------------------------

    async def play_command(self, update: Update, context):
        await self.start()

        loggin_button = await self.page.querySelector('a[href="/login"]')
        if loggin_button:
            await self.login_typing()
            await self.send_captcha_to_bot(update)
            return self.STAGE_1

        return await self.play_state_1_command(update, context)

    async def play_state_1_command(self, update: Update, context):
        if await self.check_have_captcha():
            await self.solve_captcha(update)

            is_navigated = await self.click_login_button(update)

            if not is_navigated:
                await self.resend_captcha_to_bot(update)
                return self.STAGE_1

        await self.go_to_youtube_tab()

        if await self.check_have_captcha():
            await self.send_captcha_to_bot(update)
            return self.STAGE_2

        return await self.play_state_2_command(update, context)

    async def play_state_2_command(self, update: Update, context):
        if await self.check_have_captcha():
            await self.solve_captcha(update)

            is_navigated = await self.click_submit_captcha()

            if not is_navigated:
                await self.resend_captcha_to_bot(update)
                return self.STAGE_2

        await self.play_youtube()


if __name__ == "__main__":
    pa = ProfitcentrAuto()

    async def main():
        await pa.setAccountInfo()

    # Run the asynchronous script
    asyncio.new_event_loop().run_until_complete(main())

    pa.runBot()
