import aiohttp
import json
import ssl

class MiWiFiClient:
    def __init__(self, host, username, password, session):
        self._host = host
        self._username = username
        self._password = password
        self._session = session
        self._token = None
        self.mac_address = None

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

        # SSL-Kontext erstellen und SSL-Verifizierung deaktivieren (Sicherheitsrisiko, nur in vertrauenswürdigen Netzwerken verwenden)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        try:
            async with self._session.post(url, data=data, headers=headers, ssl=ssl_context) as response:
                text = await response.text()
                print(f"Login-Antworttext: {text}")
                print(f"Antwortinhaltstyp: {response.content_type}")

                if response.status == 200:
                    # Versuche, die Antwort als JSON zu parsen
                    try:
                        result = await response.json()
                    except aiohttp.ContentTypeError:
                        result = json.loads(text)
                    if result.get("token"):
                        self._token = result.get("token")
                        print(f"Erhaltener Token: {self._token}")
                        await self.fetch_mac_address()
                        return True
                    else:
                        print(f"Login fehlgeschlagen: {result.get('msg')}")
                        return False
                else:
                    print(f"Login fehlgeschlagen. Statuscode: {response.status}")
                    return False
        except Exception as e:
            print(f"Unerwarteter Fehler beim Login: {e}")
            return False

    async def fetch_mac_address(self):
        """Methode zum Abrufen der MAC-Adresse des Routers."""
        url = f"https://{self._host}/cgi-bin/luci/api/xqdtcustom/newstatus"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        try:
            async with self._session.get(url, headers=headers, ssl=ssl_context) as response:
                if response.status == 200:
                    data = await response.json()
                    hardware_info = data.get("hardware")
                    if hardware_info:
                        self.mac_address = hardware_info.get("mac")
                        print(f"MAC-Adresse abgerufen: {self.mac_address}")
                    else:
                        print("MAC-Adresse konnte nicht in der Antwort gefunden werden.")
                else:
                    print(f"Fehler beim Abrufen der MAC-Adresse. Statuscode: {response.status}")
        except Exception as e:
            print(f"Unerwarteter Fehler beim Abrufen der MAC-Adresse: {e}")

    async def get_wan_statistics(self):
        """Hole die WAN-Statistiken."""
        return await self._get_api("xqnetwork/wan_statistics")

    async def get_device_list(self):
        """Hole die Liste der verbundenen Geräte."""
        return await self._get_api("misystem/devicelist")

    async def get_init_info(self):
        """Hole Initialisierungsinformationen."""
        return await self._get_api("xqsystem/init_info")

    async def get_wifi_display(self):
        """Hole Information zu den WLAN-Einstellungen."""
        return await self._get_api("xqdtcustom/wifi_display")

    async def get_newstatus(self):
        """Hole Custom-Status Info."""
        return await self._get_newstatus("xqdtcustom/newstatus")

    async def get_sim_info(self):
        """Hole SIM-Informationen."""
        return await self._get_sim_info("xqdtcustom/get_sim_info")

    async def get_system_info(self):
        """Hole Systeminformationen."""
        return await self._get_api("xqsystem/system_info")

    async def get_wifi_status(self):
        """Hole den Status des WLANs."""
        return await self._get_api("xqnetwork/wifi_status")

    async def get_wifi_detail(self):
        """Hole Details des WLANs."""
        return await self._get_api("xqnetwork/wifi_detail")

    async def get_wifi_detail_all(self):
        """Hole alle Details des WLANs."""
        return await self._get_api("xqnetwork/wifi_detail_all")

    async def cpe_detect(self):
        """Führe eine CPE-Erkennung durch."""
        return await self._get_api("xqdtcustom/cpe_detect")

    async def get_apn_info(self):
        """Hole die APN-Informationen."""
        return await self._get_api("xqmobile/get_apn_info")

    async def get_mobile_net_cfg(self):
        """Hole die Mobilfunknetz-Konfiguration."""
        return await self._get_api("xqmobile/get_mobile_net_cfg")

    async def _get_api(self, endpoint):
        """Hilfsmethode zum Abrufen von API-Endpunkten."""
        if not self._token:
            print("Nicht authentifiziert. Bitte zuerst einloggen.")
            return None

        url = f"https://{self._host}/cgi-bin/luci/;stok={self._token}/api/{endpoint}"

        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        # SSL-Kontext erstellen und SSL-Verifizierung deaktivieren (Sicherheitsrisiko, nur in vertrauenswürdigen Netzwerken verwenden)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        try:
            async with self._session.get(url, headers=headers, ssl=ssl_context) as response:
                text = await response.text()
                if response.status == 200:
                    # Versuche, die Antwort als JSON zu parsen
                    try:
                        result = await response.json()
                    except aiohttp.ContentTypeError:
                        result = json.loads(text)
                    return result
                else:
                    print(f"Fehler beim Abrufen von {endpoint}. Statuscode: {response.status}")
                    print(f"Antwortinhalt: {text}")
                    return None
        except Exception as e:
            print(f"Fehler beim Abrufen von {endpoint}: {e}")
            return None
