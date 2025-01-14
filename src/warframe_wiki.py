import httpx
from utils.http import HardenedHttpClient, DEFAULT_SUCCESS_CODES
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import Optional
import re


class Weapon(BaseModel):
    name: str
    url: str
    image: str | None = None
    riven_disposition: float
    mr: int | None
    weapon_type: str | None = None
    slot: str | None = None


class WarframeWiki:
    """
    A class to interact with the Warframe Wiki
    """

    def __init__(self, timeout: int = 10_000):
        self.base_url = "https://warframe.fandom.com"
        self.client = HardenedHttpClient(
            httpx.AsyncClient(timeout=timeout), success_codes=DEFAULT_SUCCESS_CODES
        )  # Initialize the HTTP client
        self.weapon_lookup = {}

    def _clean_weapon_name(self, weapon_name: str) -> str:
        """
        Clean the weapon name for use in the wiki URL
        """
        return weapon_name.replace(" ", "_").lower()

    async def weapon(self, weapon_name: str) -> Weapon:
        """
        Get the wiki page for a weapon
        """
        normalized_weapon_name = self._clean_weapon_name(weapon_name)
        if normalized_weapon_name not in self.weapon_lookup:
            return None

        url = self.base_url + self.weapon_lookup[normalized_weapon_name]
        response = await self.client.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text)

        header_contanier = soup.find("h1", id="firstHeading").find("span")
        name = header_contanier.text
        image_container = soup.find("img", class_="pi-image-thumbnail")
        image_link = (
            image_container.attrs["src"]
            if image_container and "src" in image_container.attrs
            else None
        )

        def extract_data(data_source: str) -> Optional[str]:
            parent_div = soup.find("div", attrs={"data-source": data_source})
            if parent_div:
                return parent_div.find("div", class_="pi-data-value pi-font").text
            return None

        raw_disposition = extract_data("Disposition")
        if raw_disposition:
            disposition = float(re.search(r"\(([\d\.]+)x\)", raw_disposition).group(1))
        else:
            disposition = None
        weapon_type = extract_data("Class")
        slot = extract_data("Slot")
        raw_mastery = extract_data("Mastery")
        if raw_mastery:
            mastery = int(raw_mastery)
        else:
            mastery = None

        return Weapon(
            name=name,
            url=url,
            image=image_link,
            riven_disposition=disposition,
            mr=mastery,
            weapon_type=weapon_type,
            slot=slot,
        )

    async def refresh(self):
        """
        Refresh the wiki data
        """
        self.weapon_lookup = {}
        weapon_base_url = f"{self.base_url}/wiki/Weapons#Primary"
        response = await self.client.get(weapon_base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text)
        table = soup.find("div", class_="wds-tab__content wds-is-current")
        if table:
            weapons = table.find_all("span", style="border-bottom:2px dotted; color:;")
            for weapon in weapons:
                link = weapon.find_parent("a")
                if link and "href" in link.attrs:
                    self.weapon_lookup[
                        self._clean_weapon_name(weapon.get_text().replace("\xa0", " "))
                    ] = link["href"]
