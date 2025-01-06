import httpx
import urllib.parse
from dataclasses import dataclass
from typing import Optional
import logging
from enum import Enum
import asyncio
import re
from utils.http import HardenedHttpClient, WARFRAME_API_SUCCESS_CODES


class Platform(Enum):
    PC = "PC"
    PS4 = "Playstation"
    XBOX = "Xbox"
    SWITCH = "Switch"
    UNKNOWN = "Unknown"

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
            case Platform.UNKNOWN:
                raise ValueError("Unknown platform")

    @classmethod
    def from_PUA(cls, PUA: str):
        """
        Warframe uses Unicode Private Use Area (PUA) characters at the end of usernames to denote the platform.
        This method converts the PUA character to a Platform enum.
        """
        match PUA:
            case "\ue000":
                return Platform.PC
            case "\ue001":
                return Platform.XBOX
            case "\ue002":
                return Platform.PS4
            case "\ue003":
                return Platform.SWITCH
            case _:
                return Platform.UNKNOWN


@dataclass
class Profile:
    """
    Represents a Warframe player's profile.

    Attributes:
        username (str): The player's username.
        clan (Optional[str]): The player's clan.
        mr (int): The player's mastery rank.
        multi_platform (bool): Whether the player is registered on multiple platforms.
        platform_names (dict[Platform, str]): A dictionary of the player's platform
    """

    username: str  # The player's primary username
    clan: Optional[str]
    mr: int
    multi_platform: bool
    platform_names: dict[Platform, str]


class WarframeAPI:
    """
    Class to interface with the Warframe API.
    """

    def __init__(self, timeout: int = 10_000):
        self.client = HardenedHttpClient(
            httpx.AsyncClient(timeout=timeout), success_codes=WARFRAME_API_SUCCESS_CODES
        )  # Initialize the HTTP client

    def _parse_profile(self, data: dict, source_platform: Platform) -> Profile:
        profile_data = data["Results"][0]

        is_tutorial_account = "PlayerLevel" not in profile_data
        if is_tutorial_account:
            logging.warning(
                f"Account `{profile_data['DisplayName']}` on platform `{source_platform}` is a tutorial account. Returning None!"
            )
            return None

        multi_platform = "PlatformNames" in profile_data
        if multi_platform:
            # Remove the Platform PUA character
            username = profile_data["DisplayName"][:-1].strip()

            all_platform_names = set(
                [profile_data["DisplayName"]] + profile_data["PlatformNames"]
                if multi_platform
                else []
            )
            converted_platform_names = {}
            for platform_name in all_platform_names:
                platform = Platform.from_PUA(platform_name[-1])
                converted_platform_names[platform] = platform_name[:-1].strip()
        else:
            # None multiplatform accounts will only have one platform name and dont use the PUA character
            username = profile_data["DisplayName"]
            converted_platform_names = {source_platform: username}

        mr = profile_data["PlayerLevel"]
        if "GuildName" in profile_data:
            clan = profile_data["GuildName"].split("#")[0]
        else:
            clan = None

        return Profile(
            username=username,
            mr=mr,
            clan=clan,
            multi_platform=multi_platform,
            platform_names=converted_platform_names,
        )

    def clean_username(self, username: str) -> str:
        """
        Cleans the username for usage in the API.
        """
        return username.strip().lower().replace(" ", "")

    def build_url(self, username: str, platform: Platform) -> str:
        """
        Builds the URL for the profile endpoint.
        """
        clean_username = self.clean_username(username)
        return f"{platform.url()}dynamic/getProfileViewingData.php?n={urllib.parse.quote_plus(clean_username)}"

    async def get_profile(self, username: str, platform: Platform) -> Optional[Profile]:
        logging.debug(f"Getting profile for `{username}` on platform `{platform}` ...")
        url = self.build_url(username, platform)
        response = await self.client.get(url)

        # Check if we got a 409 response, this can happen if the user has linked their account to a different platform
        if response.status_code == 409:
            try:
                message = response.text
                match = re.search(
                    r"Retry with (\w+) account: ([a-f0-9]+),(\w+)", message
                )
                if match:
                    platform = Platform(match.group(1))
                    master_username = match.group(3)
                    # Retry with the new platform
                    logging.info(
                        f"Retrying profile `{username}` with platform: {platform} and username: {master_username}"
                    )
                    return await self.get_profile(master_username, platform)
                else:
                    logging.info(
                        f"Didn't find user `{username}` on platform {platform}"
                    )
                    return None
            except Exception as e:
                logging.error(
                    f"Failed to parse platform from message: {message} with error: {e}"
                )
        try:
            response.raise_for_status()
            return self._parse_profile(response.json(), source_platform=platform)
        except httpx.HTTPError as e:
            logging.error(
                f"Failed to get profile `{username}` on platform `{platform}`: {e}"
            )
        return None

    async def get_profile_all_platforms(self, username: str) -> Optional[Profile]:
        tasks = []
        for platform in Platform:
            if platform == Platform.UNKNOWN:
                continue
            tasks.append(self.get_profile(username, platform))

        result = await asyncio.gather(*tasks)
        for profile in result:
            if profile:
                return profile

        return None
