from asyncio import sleep
from telegram import Bot
from profiles_handler import Profiles
from translate import Translator


def translate_text(text, source_language, target_language):
    translator = Translator(to_lang=target_language, from_lang=source_language)
    translation = translator.translate(text)
    return translation


default_options = {
    "username": "ngmitr2512@gmail.com",
    "password": "fn7n6yr",
    "cookie": "",
    "profile_id": "69927",
}


class ProfitcentrAuto:
    def __init__(self, options=default_options) -> None:
        self.login_url = "https://profitcentr.com/login"
        self.url = "https://profitcentr.com"
        self.page = None

        self.username = options.get("username")
        self.password = options.get("password")
        self.cookie = options.get("cookie")
        self.profile_id = options.get("profile_id")

    async def start(self):
        p = Profiles()
        p.setProfileId(self.profile_id)

        browser = await p.start()
        page = await browser.newPage()

        await page.goto(self.url)
        await sleep(3)
        self.page = page

    async def add_cookie(self):
        await self.page.setCookie(self.cookie)

    async def get_capcha_title(self):
        element = await self.page.querySelector("#login-form")
        if element:
            capcha_title = await self.get_element_content(
                "#login-form .out-capcha-title"
            )
            translated_capcha_title = translate_text(capcha_title, "ru", "vi")

            return translated_capcha_title
        else:
            return "Not found login form"

    async def fill_login(self, info):
        await self.page.type("#login-form input[name='username']", self.username)

        await self.page.type("#login-form input[name='password']", self.password)

    async def click_login(self):
        await self.page.click("#login-form button")

    async def get_element_content(self, selector):
        await self.page.waitForSelector(selector)

        element_content = await self.page.evaluate(
            f'document.querySelector("{selector}").textContent'
        )

        return element_content.strip()

    async def click_menu(self):
        self.page.click("#mnu_title1")
