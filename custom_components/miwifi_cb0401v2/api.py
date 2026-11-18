import aiohttp
import json
import ssl
import logging

_LOGGER = logging.getLogger(__name__)

class MiWiFiClient:
    def __init__(self, host, username, password, session):
        self._host = host
        self._username = username
        self._password = password
        self._session = session
        self._token = None
        self.mac_address = None
        self.firmware_version = None 
        self._in_login = False

    async def login(self):
        """Authenticate and getting token."""
        if self._in_login:
            return False
        self._in_login = True
        try:
            return await self._login()
        finally:
            self._in_login = False

    async def _login(self):
        url = f"https://{self._host}/cgi-bin/luci/api/xqsystem/login"
        data = {
            "username": self._username,
            "logtype": 2,
            "password": self._password  # Klartext-Passwort
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        ssl_context = False  # SSL-Prüfung deaktiviert

        try:
            async with self._session.post(url, data=data, headers=headers, ssl=ssl_context) as response:
                text = await response.text()
                if response.status == 200:
                    try:
                        result = await response.json()
                    except aiohttp.ContentTypeError:
                        result = json.loads(text)
                    if result.get("token"):
                        self._token = result.get("token")
                        _LOGGER.debug("Login successful, token received")
                        await self.fetch_mac_address()
                        await self.fetch_init_info()  # Hole Firmware-Version und andere Initialdaten
                        return True
                    else:
                        _LOGGER.error(f"Login error: {result.get('msg')}")
                        return False
                else:
                    _LOGGER.error(f"Login error: {response.status}")
                    return False
        except Exception as e:
            _LOGGER.error(f"Unknown error while login: {e}")
            return False

    async def fetch_mac_address(self):
        """Method for requesting MAC-address."""
        url = f"https://{self._host}/cgi-bin/luci/;stok={self._token}/api/xqdtcustom/newstatus"
        headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
        ssl_context = False
        
        try:
            async with self._session.get(url, headers=headers, ssl=ssl_context) as response:
                if response.status == 200:
                    text = await response.text()
                    data = json.loads(text)
                    hardware_info = data.get("hardware")
                    if hardware_info:
                        self.mac_address = hardware_info.get("mac")
                        _LOGGER.debug(f"Successfully requested MAC-address: {self.mac_address}")
                    else:
                        _LOGGER.warning("MAC-Adresse could'nt found in the JSON answer.")
                else:
                    _LOGGER.error(f"Error while requesting MAC-address. Statuscode: {response.status}")
        except Exception as e:
            _LOGGER.error(f"Error while requesting MAC-address: {e}")

    async def fetch_init_info(self):
        """Getting initial informations"""
        data = await self.get_init_info()
        if data:
            self.firmware_version = data.get("romversion")
            _LOGGER.debug(f"Firmware-Version: {self.firmware_version}")

    async def cpe_detect(self):
        """Choose cpe_detect api endpoint"""
        return await self._get_api("xqdtcustom/cpe_detect")

    async def newstatus(self):
        """Choose newstatus api endpoint"""
        return await self._get_api("xqdtcustom/newstatus")

    async def get_init_info(self):
        """Choose init_info api endpoint"""
        return await self._get_api("xqsystem/init_info")

    async def devicelist(self):
        """Choose devicelist api endpoint"""
        return await self._get_api("misystem/devicelist")

    async def msgbox_count(self):
        """Choose get_msgbox_count api endpoint"""
        return await self._get_api("xqmobile/get_msgbox_count")

    async def _get_api(self, endpoint, _retry=True):
        """Helper for API requests.

        The router invalidates the stok token after some time (or after a
        router reboot). On an "Invalid token" answer (HTTP 401 or JSON
        code 401) log in again once and repeat the request.
        """
        if not self._token:
            if not _retry or not await self.login():
                _LOGGER.error("Not authenticated, login failed.")
                return None

        url = f"https://{self._host}/cgi-bin/luci/;stok={self._token}/api/{endpoint}"
        headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
        ssl_context = False

        try:
            async with self._session.get(url, headers=headers, ssl=ssl_context) as response:
                text = await response.text()
                result = None
                if response.status in (200, 401):
                    try:
                        result = json.loads(text)
                    except ValueError:
                        result = None
                if response.status == 401 or (isinstance(result, dict) and result.get("code") == 401):
                    if _retry:
                        _LOGGER.debug("Token expired while requesting %s, logging in again", endpoint)
                        self._token = None
                        if await self.login():
                            return await self._get_api(endpoint, _retry=False)
                    _LOGGER.error("Token rejected while requesting %s", endpoint)
                    return None
                if response.status == 200 and result is not None:
                    return result
                else:
                    _LOGGER.error(f"Error while request {endpoint}. Statuscode: {response.status}")
                    _LOGGER.debug(f"Answer: {text}")
                    return None
        except Exception as e:
            _LOGGER.error(f"Error while request {endpoint}: {e}")
            return None
