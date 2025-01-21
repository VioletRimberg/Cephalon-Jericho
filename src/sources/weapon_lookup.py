from pydantic import BaseModel
import difflib
from model.rivens import RivenEffect
from typing import Optional


class WantedRivenStats(BaseModel):
    best: Optional[list[RivenEffect]]
    wanted: Optional[list[RivenEffect]]
    wanted_negatives: Optional[list[RivenEffect]]


class RivenRecommendations(BaseModel):
    weapon: str
    comment: Optional[str]
    stats: list[WantedRivenStats]


class WeaponLookupEntry(BaseModel):
    display_name: str
    wiki_url: str
    normalized_name: str
    riven_recommendations: Optional[RivenRecommendations] = None
    median_plat_price: Optional[float] = None
    weapon_variants: Optional[list[str]] = None
    base_weapon: Optional[str] = None

    @property
    def is_base_weapon(self):
        return self.base_weapon is None

    @property
    def can_have_rivens(self):
        return self.riven_recommendations is not None

    def get_market_auction_url(self):
        """
        Return the URL for the weapon's riven market auctions
        """
        if not self.can_have_rivens:
            return None

        wf_market_weapon_name = (
            self.display_name.replace(" ", "_").replace("&", "and").lower().strip()
        )
        return f"https://warframe.market/auctions/search?type=riven&weapon_url_name={wf_market_weapon_name}&polarity=any&sort_by=price_asc"


class WeaponLookup:
    """
    A unified weapon lokup class to collect displaynames and URLs for weapons
    """

    def __init__(self):
        self.weapon_lookup: dict[str, WeaponLookupEntry] = {}

    def _normalize_weapon_name(self, weapon_name: str) -> str:
        return weapon_name.replace(" ", "_").lower()

    def add(self, weapon_name: str, url: str):
        normalized_name = self._normalize_weapon_name(weapon_name)
        self.weapon_lookup[normalized_name] = WeaponLookupEntry(
            display_name=weapon_name, wiki_url=url, normalized_name=normalized_name
        )

    def __getitem__(self, key: str) -> WeaponLookupEntry:
        normalized = self._normalize_weapon_name(key)
        return self.weapon_lookup[normalized]

    def __contains__(self, key: str) -> bool:
        normalized = self._normalize_weapon_name(key)
        return normalized in self.weapon_lookup

    def __len__(self):
        return len(self.weapon_lookup)

    def fuzzy_search(
        self, weapon_name: str, n: int = 20, cutoff=0.35, can_have_rivens: bool = False
    ) -> list[WeaponLookupEntry]:
        if can_have_rivens:
            weapon_names = [
                w.display_name for w in self.weapon_lookup.values() if w.can_have_rivens
            ]
        else:
            weapon_names = [w.display_name for w in self.weapon_lookup.values()]
        matches = difflib.get_close_matches(
            weapon_name, weapon_names, n=n, cutoff=cutoff
        )
        if len(matches) > 0:
            return [self[match] for match in matches]
        return []

    def rebuild_weapon_relations(self):
        """
        Rebuild the weapon relations for all weapons in the lookup
        """
        for weapon in self.weapon_lookup.values():
            weapon_name = weapon.normalized_name
            without_prefix = "_".join(weapon_name.split("_")[1:])
            without_postfix = "_".join(weapon_name.split("_")[:-1])

            for potential_base in [without_prefix, without_postfix]:
                # Handle weapons without prefixes or postfixes
                if potential_base == weapon_name:
                    continue

                # check if the potential_base is in the lookup
                if potential_base in self.weapon_lookup:
                    base_weapon = self.weapon_lookup[potential_base]
                    # link the weapon to the base weapon
                    weapon.base_weapon = base_weapon.normalized_name

                    # set the riven recommendations of the weapon if the base weapon has riven recommendations
                    if base_weapon.riven_recommendations is not None:
                        weapon.riven_recommendations = base_weapon.riven_recommendations

                    # add the weapon variant to the base weapons variants
                    if base_weapon.weapon_variants is None:
                        base_weapon.weapon_variants = []
                    base_weapon.weapon_variants.append(weapon.normalized_name)
