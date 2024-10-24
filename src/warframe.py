import httpx
import urllib.parse
from dataclasses import dataclass
from typing import Optional
import logging

@dataclass
class Profile:
    """
    Represents a Warframe player's profile.

    Attributes:
        username (str): The player's username.
        clan (str): The player's clan.
        mr (int): The player's mastery rank.
    """

    username: str
    clan: str
    mr: int


class WarframeAPI:
    """
    Class to interface with the Warframe API.
    """
    def __init__(self, timeout: int = 5_000):
        self.client = httpx.AsyncClient(timeout=timeout)  # Initialize the HTTP client

    def _parse_profile(self, data: dict) -> Profile:
        profile_data = data["Results"][0]

        username = profile_data["DisplayName"].replace("\ue000", "").strip()
        mr = profile_data["PlayerLevel"]
        clan = profile_data["GuildName"].split("#")[0]

        return Profile(username=username, mr=mr, clan=clan)

    async def get_profile(self, username: str) -> Optional[Profile]:
        url = f"https://content.warframe.com/dynamic/getProfileViewingData.php?n={urllib.parse.quote_plus(username)}"
        response = await self.client.get(url)
        try:
            response.raise_for_status()
            return self._parse_profile(response.json())
        except httpx.HTTPError as e:
            logging.error(f"Failed to get profile `{username}`: {e}") 
        return None


async def main():
    api = WarframeAPI()
    profile = await api.get_profile("LLukas22")
    print(profile)  # Print the profile data


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
