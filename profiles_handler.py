from asyncio import sleep
from gologin import GoLogin
from utils import *
from info_utils import *
from pyppeteer import launch

default_create_options = {
    "name": "o",
    "os": "mac",
    "navigator": {
        "language": "en-US",
        "userAgent": "random",
        "resolution": "1920x1080",
        "platform": "mac",
    },
    "proxy": {
        "mode": "none",
        # "host": '',
        # "port": '',
        # "username": '',
        # "password": '',
    },
    "webRTC": {
        "mode": "alerted",
        "enabled": True,
    },
    "storage": {
        "local": True,  # Local Storage is special browser caches that websites may use for user tracking in a way similar to cookies.
        # Having them enabled is generally advised but may increase browser profile loading times.
        "extensions": True,  # Extension storage is a special cotainer where a browser stores extensions and their parameter.
        # Enable it if you need to install extensions from a browser interface.
        "bookmarks": True,  # This option enables saving bookmarks in a browser interface.
        "history": True,  # Warning! Enabling this option may increase the amount of data required
        # to open/save a browser profile significantly.
        # In the interests of security, you may wish to disable this feature,
        # but it may make using GoLogin less convenient.
        "passwords": True,  # This option will save passwords stored in browsers.
        # It is used for pre-filling login forms on websites.
        # All passwords are securely encrypted alongside all your data.
        "session": True,  # This option will save browser session. It is used to save last open tabs.
        "indexedDb": False  # IndexedDB is special browser caches that websites may use for user tracking in a way similar to cookies.
        # Having them enabled is generally advised but may increase browser profile loading times.
    },
}

default_init_options = {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTk3OWJkMGViOWU2M2YzNDcwZDU5MjMiLCJ0eXBlIjoiZGV2Iiwiand0aWQiOiI2NTlkMmQwOTc3NDJjNTdiYTg1ZWJkNzUifQ.gXbYZNg6NqNNTm301zzlg7cjsBedsB7hCadje8jzq8s",
    "profiles_path": "C:\\Users\\xinch\\Desktop\\1.Projects\\auto-browser\\Profiles",
    "profiles_info_path": "C:\\Users\\xinch\\Desktop\\1.Projects\\auto-browser\\Profiles\\info.json",
    "executablePath": "C:/Users/xinch/.gologin/browser/orbita-browser-120/chrome.exe",
    "create_options": default_create_options,
}

default_info = {
    "name": "",
    "id": "",
    "tag": ["", ""],
    "notes": "",
    "proxy": {"type": "none", "host": "", "port": "", "username": "", "password": ""},
}


class Profiles:
    def __init__(self, options=default_init_options):
        self.token = options.get("token")
        self.profiles_path = options.get("profiles_path")
        self.profiles_info_path = options.get("profiles_info_path")
        self.create_options = options.get("create_options")
        self.executablePath = options.get("executablePath")

        self.profile_id: str
        self.Info = Info(self.profiles_info_path)

    def setProfileId(self, profile_id):
        self.profile_id = profile_id

    async def getAllProfileId(self):
        return get_folder_names(self.profiles_path)

    async def updateProfileName(self, new_profile_name):
        update_item_name(self.profiles_info_path, self.profile_id, new_profile_name)
        return print(f"Update name successfully")

    async def delete(self, profile_id):
        if not profile_id:
            profile_id = self.profile_id

        delete_folder(self.profiles_path, profile_id)
        self.Info.delete(profile_id)

        return print(f"delete profile {profile_id} successfully")

    async def create(self, info=default_info):
        gl = GoLogin({"token": self.token})

        profile_id = gl.create(self.create_options)

        gl.setProfileId(profile_id)

        gl.start()

        await sleep(1)

        gl_profile_path = gl.profile_path

        profile_id = str(generate_random_number())

        copy_and_rename_folder(gl_profile_path, self.profiles_path, profile_id)

        gl.stop()
        gl.delete()

        self.profile_id = profile_id

        info["id"] = info["name"] = self.profile_id

        self.Info.add(info)

        print(info)

        return info

    async def start(self):
        profile_path = get_folder_path(self.profiles_path, self.profile_id)
        browser = await launch(
            {
                "executablePath": self.executablePath,
                "userDataDir": profile_path,
                "headless": False,
            }
        )
        page = await browser.newPage()
        await sleep(3)

        return browser

    async def getAllProfileInfo(self):
        all_info = self.Info.get_all_info()
        print("all profiles info:", all_info)
        return all_info
