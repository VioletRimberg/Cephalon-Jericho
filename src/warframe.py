import httpx
# changing to json5 from json due to output issues from the warframe API giving no proper JSON files
import json5
from sources import WeaponLookup
from utils.http import HardenedHttpClient, WARFRAME_API_SUCCESS_CODES


class WarframeAPI:
    """
    Class to interface with the Warframe API.
    """

    def __init__(self, timeout: int = 10_000):
        self.client = HardenedHttpClient(
            httpx.AsyncClient(timeout=timeout),
            success_codes=WARFRAME_API_SUCCESS_CODES
        )

    async def get_median_prices(self, weapon_lookup: WeaponLookup):
        result = await self.client.get(
            "https://www-static.warframe.com/repos/weeklyRivensPC.json"
        )

        result.raise_for_status()

        raw_text = result.text

        # Sanity check 
        if not raw_text or len(raw_text) < 20:
            raise ValueError("Warframe API returned empty or invalid response")

        try:
            data = json5.loads(raw_text)
        except json5.JSONDecodeError as e:
            # For Parsing Failure
            print("JSON parsing failed")
            print("First 300 chars of response:")
            print(raw_text[:300])
            raise e

        # normalize safety
        if isinstance(data, dict):
            data = data.get("payload", data)

        for item in data:
            compatibility = item.get("compatibility")
            if not compatibility:
                continue

            if compatibility not in weapon_lookup:
                continue

            weapon_lookup[compatibility].median_plat_price = item.get("median")