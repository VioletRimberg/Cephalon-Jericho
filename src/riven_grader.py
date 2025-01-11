from model.rivens import Riven, RivenEffect
from model.weapon import WeaponModType
from sources import WarframeWiki
from typing import Optional


class RivenGrader:
    def __init__(self, wiki: WarframeWiki):
        self.wiki = wiki

    async def valdiate(self, riven: Riven) -> tuple[bool, Optional[str]]:
        """
        Check if the provided riven can exist and report any issues.
        """

        try:
            # check if the riven has a valide amount of positives / negatives
            riven_type = riven.riven_type
        except ValueError as e:
            return False, str(e)

        # get the weapon from the wiki
        weapon = await self.wiki.weapon(riven.weapon)
        if weapon is None:
            return False, f"Could not find weapon `{riven.weapon}`"

        # check if the weapon type can have a riven (Mainly filters out Railjack weapons)
        if weapon.mod_type == WeaponModType.Misc:
            return (
                False,
                f"Weapon `{riven.weapon}` can't have a riven because it's mod type is `{weapon.mod_type.value}`!",
            )

        stat_errors = []
        for (riven_effect, value), is_pos in riven.all_stats:
            riven_effect: RivenEffect = riven_effect
            value: float = value
            # Check if this stat is valid for the weapon type
            if not riven_effect.valid_on_mod_type(weapon.mod_type.value):
                stat_errors.append(
                    f"Stat `{riven_effect.value}` is not valid for weapon `{riven.weapon}` of type `{weapon.mod_type.value}`"
                )
                continue

            compensated_value = value
            # Check if the value is within the valid range
            min_value, max_value = riven_effect.calculate_range(
                weapon.riven_disposition.disposition,
                weapon.mod_type,
                riven_type,
                is_negative=not is_pos,
            )
            if compensated_value < min_value or compensated_value > max_value:
                stat_errors.append(
                    f"Stat `{riven_effect.value}` with value `{value}` is out of range for weapon `{riven.weapon}` of type `{weapon.mod_type.value}`. Expected range: {min_value} - {max_value}"
                )

        if len(stat_errors) > 0:
            return False, "\n".join(stat_errors)

        return True, None
