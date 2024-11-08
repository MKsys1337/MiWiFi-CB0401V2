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
        self.firmware_version = None  # Wird nach erfolgreichem Login aus init_info gesetzt

    async def login(self):
        """Authentifiziere dich beim Router und erhalte einen Token."""
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
                        _LOGGER.debug(f"Erhaltener Token: {self._token}")
                        await self.fetch_mac_address()
                        await self.fetch_init_info()  # Hole Firmware-Version und andere Initialdaten
                        return True
                    else:
                        _LOGGER.error(f"Login fehlgeschlagen: {result.get('msg')}")
                        return False
                else:
                    _LOGGER.error(f"Login fehlgeschlagen. Statuscode: {response.status}")
                    return False
        except Exception as e:
            _LOGGER.error(f"Unerwarteter Fehler beim Login: {e}")
            return False

    async def fetch_mac_address(self):
        """Methode zum Abrufen der MAC-Adresse des Routers."""
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
                        _LOGGER.debug(f"MAC-Adresse erfolgreich abgerufen: {self.mac_address}")
                    else:
                        _LOGGER.warning("MAC-Adresse konnte nicht im Antwort-JSON gefunden werden.")
                else:
                    _LOGGER.error(f"Fehler beim Abrufen der MAC-Adresse. Statuscode: {response.status}")
        except Exception as e:
            _LOGGER.error(f"Unerwarteter Fehler beim Abrufen der MAC-Adresse: {e}")

    async def fetch_init_info(self):
        """Hole Initialisierungsinformationen, wie Firmware-Version und Modell."""
        data = await self.get_init_info()
        if data:
            self.firmware_version = data.get("romversion")
            _LOGGER.debug(f"Firmware-Version: {self.firmware_version}")

    async def cpe_detect(self):
        """Führe eine CPE-Erkennung durch."""
        return await self._get_api("xqdtcustom/cpe_detect")

    async def get_init_info(self):
        """Hole Initialisierungsinformationen."""
        return await self._get_api("xqsystem/init_info")

    async def _get_api(self, endpoint):
        """Hilfsmethode zum Abrufen von API-Endpunkten."""
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
                    _LOGGER.error(f"Fehler beim Abrufen von {endpoint}. Statuscode: {response.status}")
                    _LOGGER.debug(f"Antwortinhalt: {text}")
                    return None
        except Exception as e:
            _LOGGER.error(f"Fehler beim Abrufen von {endpoint}: {e}")
            return None
