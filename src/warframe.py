import httpx
from sources import WeaponLookup
from utils.http import HardenedHttpClient, WARFRAME_API_SUCCESS_CODES


class WarframeAPI:
    """
    Class to interface with the Warframe API.
    """

    def __init__(self, timeout: int = 10_000):
        self.client = HardenedHttpClient(
            httpx.AsyncClient(timeout=timeout), success_codes=WARFRAME_API_SUCCESS_CODES
        )  # Initialize the HTTP client

    async def get_median_prices(self, weapon_lookup: WeaponLookup):
        result = await self.client.get(
            "https://www-static.warframe.com/repos/weeklyRivensPC.json"
        )
        result.raise_for_status()
        data = result.json()
        for item in data:
            if "compatibility" not in item:
                continue
            if (
                item["compatibility"] is None
                or item["compatibility"] not in weapon_lookup
            ):
                continue

            weapon_lookup[item["compatibility"]].median_plat_price = item["median"]
