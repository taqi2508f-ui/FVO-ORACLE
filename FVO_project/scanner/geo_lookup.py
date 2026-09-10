import requests
import socket
from typing import Optional, Dict


COUNTRY_COORDS = {
    "US": (39.5, -98.35), "CN": (35.86, 104.19), "RU": (61.52, 105.31),
    "DE": (51.16, 10.45), "GB": (55.37, -3.43), "FR": (46.22, 2.21),
    "JP": (36.20, 138.25), "IN": (20.59, 78.96), "BR": (14.23, -51.92),
    "CA": (56.13, -106.34), "AU": (-25.27, 133.77), "KR": (35.90, 127.76),
    "IT": (41.87, 12.56), "ES": (40.46, -3.74), "NL": (52.13, 5.29),
    "SE": (60.12, 18.64), "NO": (60.47, 8.46), "CH": (46.81, 8.22),
    "PL": (51.91, 19.14), "UA": (48.37, 31.16), "TR": (38.96, 35.24),
    "SA": (23.88, 45.07), "IL": (31.04, 34.85), "ZA": (30.55, 22.93),
    "NG": (9.08, 8.67), "EG": (26.82, 30.80), "MX": (23.63, -102.55),
    "AR": (38.41, -63.61), "CL": (35.67, -71.54), "CO": (4.57, -74.29),
    "ID": (0.78, 113.92), "MY": (4.21, 101.97), "SG": (1.35, 103.81),
    "TH": (15.87, 100.99), "VN": (14.05, 108.27), "PH": (12.87, 121.77),
    "PK": (30.37, 69.34), "BD": (23.68, 90.35), "IR": (32.42, 53.68),
    "IQ": (33.22, 43.67), "AE": (23.42, 53.84), "NZ": (40.90, 174.88),
    "FI": (61.92, 25.74), "DK": (56.26, 9.50), "BE": (50.50, 4.46),
    "AT": (47.51, 14.55), "PT": (39.39, -8.22), "GR": (39.07, 21.82),
    "CZ": (49.81, 15.47), "HU": (47.16, 19.50), "RO": (45.94, 24.96),
    "BG": (42.73, 25.48), "HR": (45.10, 15.20), "SK": (48.66, 19.69),
    "LT": (55.16, 23.88), "LV": (56.87, 24.60), "EE": (58.59, 25.01),
    "BY": (53.70, 27.95), "KZ": (48.01, 66.92), "UZ": (41.37, 64.58),
}

FLAG_EMOJIS = {
    "US": "🇺🇸", "CN": "🇨🇳", "RU": "🇷🇺", "DE": "🇩🇪", "GB": "🇬🇧",
    "FR": "🇫🇷", "JP": "🇯🇵", "IN": "🇮🇳", "BR": "🇧🇷", "CA": "🇨🇦",
    "AU": "🇦🇺", "KR": "🇰🇷", "IT": "🇮🇹", "ES": "🇪🇸", "NL": "🇳🇱",
    "SE": "🇸🇪", "NO": "🇳🇴", "CH": "🇨🇭", "PL": "🇵🇱", "UA": "🇺🇦",
    "TR": "🇹🇷", "SA": "🇸🇦", "IL": "🇮🇱", "ZA": "🇿🇦", "NG": "🇳🇬",
    "EG": "🇪🇬", "MX": "🇲🇽", "AR": "🇦🇷", "SG": "🇸🇬", "AE": "🇦🇪",
    "ID": "🇮🇩", "PK": "🇵🇰", "IR": "🇮🇷", "NZ": "🇳🇿",
}


class GeoLookup:
    def __init__(self):
        self._cache: Dict[str, Dict] = {}

    def lookup(self, ip: str) -> Optional[Dict]:
        if ip in self._cache:
            return self._cache[ip]

        if self._is_private(ip):
            result = {
                "ip": ip, "country": "Local Network", "countryCode": "LAN",
                "city": "Private", "region": "LAN", "isp": "Private Network",
                "lat": 0.0, "lon": 0.0, "org": "Local",
                "flag": "🏠", "timezone": "Local"
            }
            self._cache[ip] = result
            return result

        try:
            r = requests.get(
                f"http://ip-api.com/json/{ip}"
                "?fields=status,country,countryCode,region,regionName,city,"
                "lat,lon,isp,org,timezone,query",
                timeout=6
            )
            if r.status_code == 200:
                data = r.json()
                if data.get("status") == "success":
                    code = data.get("countryCode", "")
                    result = {
                        "ip": ip,
                        "country": data.get("country", "Unknown"),
                        "countryCode": code,
                        "city": data.get("city", ""),
                        "region": data.get("regionName", ""),
                        "isp": data.get("isp", ""),
                        "org": data.get("org", ""),
                        "lat": data.get("lat", 0.0),
                        "lon": data.get("lon", 0.0),
                        "timezone": data.get("timezone", ""),
                        "flag": FLAG_EMOJIS.get(code, "🌐"),
                    }
                    self._cache[ip] = result
                    return result
        except Exception:
            pass

        result = {
            "ip": ip, "country": "Unknown", "countryCode": "??",
            "city": "", "region": "", "isp": "", "org": "",
            "lat": 0.0, "lon": 0.0, "timezone": "", "flag": "🌐"
        }
        self._cache[ip] = result
        return result

    def _is_private(self, ip: str) -> bool:
        try:
            parts = list(map(int, ip.split(".")))
            if parts[0] == 10: return True
            if parts[0] == 127: return True
            if parts[0] == 172 and 16 <= parts[1] <= 31: return True
            if parts[0] == 192 and parts[1] == 168: return True
            if parts[0] == 169 and parts[1] == 254: return True
        except Exception:
            pass
        return False
