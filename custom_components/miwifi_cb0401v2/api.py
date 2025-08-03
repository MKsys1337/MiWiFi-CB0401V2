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

    async def login(self):
        """Authenticate and getting token."""
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
                        _LOGGER.debug(f"Requested Token: {self._token}")
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

    async def _get_api(self, endpoint):
        """Helper for API requests"""
        if not self._token:
            _LOGGER.error("Nicht authentifiziert. Bitte zuerst einloggen.")
            return None

        url = f"https://{self._host}/cgi-bin/luci/;stok={self._token}/api/{endpoint}"
        headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
        ssl_context = False

        try:
            async with self._session.get(url, headers=headers, ssl=ssl_context) as response:
                text = await response.text()
                if response.status == 200:
                    try:
                        result = await response.json()
                    except aiohttp.ContentTypeError:
                        result = json.loads(text)
                    return result
                else:
                    _LOGGER.error(f"Error while request {endpoint}. Statuscode: {response.status}")
                    _LOGGER.debug(f"Answer: {text}")
                    return None
        except Exception as e:
            _LOGGER.error(f"Error while request {endpoint}: {e}")
            return None
