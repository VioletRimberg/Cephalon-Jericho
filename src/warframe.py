import httpx
import urllib.parse
from dataclasses import dataclass
from typing import Optional
import logging
from enum import Enum
import asyncio

class Platform(Enum):
    PC = "PC"
    PS4 = "Playstation"
    XBOX = "Xbox"
    SWITCH = "Switch"

    def url(self):
        """
        Returns the URL for the platform's endpoints.
        """
        match self:
            case Platform.PC:
                return "https://content.warframe.com/"
            case Platform.PS4:
                return "https://content-ps4.warframe.com/"
            case Platform.XBOX:
                return "https://content-xb1.warframe.com/"
            case Platform.SWITCH:
                return "https://content-swi.warframe.com/"


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

    def __init__(self, timeout: int = 10_000):
        self.client = httpx.AsyncClient(timeout=timeout)  # Initialize the HTTP client

    def _parse_profile(self, data: dict) -> Profile:
        try:
            profile_data = data["Results"][0]

            username = profile_data["DisplayName"].replace("\ue000", "").strip()
            mr = profile_data["PlayerLevel"]
            clan = profile_data["GuildName"].split("#")[0]

            return Profile(username=username, mr=mr, clan=clan)
        except Exception as _:
            # On some platforms we get a cut down version of the profile since it was linked to a master account on PC
            return None

    def clean_username(self, username: str) -> str:
        """
        Cleans the username for usage in the API.
        """
        return username.strip().lower().replace(" ", "")

    async def get_profile(self, username: str, platform: Platform) -> Optional[Profile]:
        clean_username = self.clean_username(username)
        url = f"{platform.url()}dynamic/getProfileViewingData.php?n={urllib.parse.quote_plus(clean_username)}"
        response = await self.client.get(url)
        try:
            response.raise_for_status()
            return self._parse_profile(response.json())
        except httpx.HTTPError as e:
            logging.error(f"Failed to get profile `{username}`: {e}")
        return None

    async def get_profile_all_platforms(
        self, username: str
    ) -> Optional[tuple[Profile, Platform]]:
        tasks = []
        for platform in Platform:
            tasks.append(self.get_profile(username, platform))

        result = await asyncio.gather(*tasks)
        for profile, platform in zip(result, Platform):
            if profile:
                return profile, platform

        return None
