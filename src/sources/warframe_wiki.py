import httpx
from utils.http import HardenedHttpClient, DEFAULT_SUCCESS_CODES
from model.weapon import Weapon, RivenDisposition, WeaponModType
from bs4 import BeautifulSoup
from typing import Optional
import re
from .weapon_lookup import WeaponLookup


class WarframeWiki:
    """
    A class to interact with the Warframe Wiki
    """

    def __init__(
        self, weapon_lookup: WeaponLookup = WeaponLookup(), timeout: int = 10_000
    ):
        self.base_url = "https://wiki.warframe.com"
        self.client = HardenedHttpClient(
            httpx.AsyncClient(timeout=timeout), success_codes=DEFAULT_SUCCESS_CODES
        )  # Initialize the HTTP client
        self.weapon_lookup = weapon_lookup

    async def weapon(self, weapon_name: str) -> Weapon:
        """
        Get the wiki page for a weapon
        """
        if weapon_name not in self.weapon_lookup:
            return None

        url = self.base_url + self.weapon_lookup[weapon_name].wiki_url
        response = await self.client.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, features="html.parser")

        header_contanier = soup.find("h1", id="firstHeading").find("span")
        name = header_contanier.text

        image_span = soup.find("span", class_="main-image")
        image_link = None
        if image_span:
            image_container = image_span.find("img")
            image_link = (
                self.base_url + image_container.attrs["src"]
                if image_container and "src" in image_container.attrs
                else None
            )

        def extract_data(data_source: str) -> Optional[str]:
            link_a = soup.find("a", text=data_source)
            if link_a:
                row = link_a.find_parent("div").find_parent("div")
                value_column = row.find("div", class_="value")
                if value_column:
                    return value_column.text
            return None

        raw_disposition = extract_data("Disposition")
        match = re.search(r"([●○]+)\s\(([\d\.]+)x\)", raw_disposition)
        if match:
            disposition_symbol = match.group(1)
            disposition_value = float(match.group(2))
            disposition = RivenDisposition(
                disposition=disposition_value, symbol=disposition_symbol
            )
        else:
            disposition = RivenDisposition()
        weapon_type = extract_data("Type")
        slot = extract_data("Slot")
        raw_mastery = extract_data("Mastery Rank Requirement")
        if raw_mastery:
            mastery = int(raw_mastery)
        else:
            mastery = None
        mod_type = WeaponModType.from_raw_data(slot, weapon_type)

        return Weapon(
            name=name,
            url=url,
            image=image_link,
            riven_disposition=disposition,
            mr=mastery,
            weapon_type=weapon_type,
            slot=slot,
            mod_type=mod_type,
        )

    def mark_riven_capable(self, weapon_name: str):
        """
        Mark a weapon as riven capable
        """
        if weapon_name in self.weapon_lookup:
            self.weapon_lookup[weapon_name].can_have_rivens = True

    async def refresh(self):
        """
        Refresh the wiki data
        """
        weapon_base_url = f"{self.base_url}/w/Weapons#Primary"
        response = await self.client.get(weapon_base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, features="html.parser")
        table = soup.find("div", class_="tabber")
        if table:
            weapons = table.find_all("span", style="border-bottom:2px dotted; color:;")
            for weapon in weapons:
                link = weapon.find_parent("a")
                if link and "href" in link.attrs:
                    self.weapon_lookup.add(
                        weapon.get_text().replace("\xa0", " "), link["href"]
                    )

        # Manually add the kitgun chambers since they are not in the weapon list
        self.weapon_lookup.add("Catchmoon", "/w/Catchmoon")
        self.weapon_lookup.add("Gaze", "/w/Gaze")
        self.weapon_lookup.add("Rattleguts", "/w/Rattleguts")
        self.weapon_lookup.add("Sporelacer", "/w/Sporelacer")
        self.weapon_lookup.add("Tombfinger", "/w/Tombfinger")
        self.weapon_lookup.add("Vermisplicer", "/w/Vermisplicer")
        # Ok no idea why this isnt in the weapon list but we need to add it
        self.weapon_lookup.add("Dark Split-Sword", "/w/Dark_Split-Sword")
