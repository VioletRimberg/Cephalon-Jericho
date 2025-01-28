from pydantic import BaseModel
from typing import Optional
from enum import Enum


class WeaponModType(str, Enum):
    Rifle = "Rifle"
    Shotgun = "Shotgun"
    Pistol = "Pistol"
    Archgun = "Archgun"
    Melee = "Melee"
    Misc = "Misc"  # For stuff like railjack weapons, etc.

    @classmethod
    def from_raw_data(cls, slot: str, weapon_type: str) -> "WeaponModType":
        if weapon_type == "Shotgun":
            return WeaponModType.Shotgun
        elif weapon_type == "Glaive":
            return WeaponModType.Melee
        elif slot == "Primary":
            return WeaponModType.Rifle
        elif slot == "Secondary":
            return WeaponModType.Pistol
        elif slot == "Melee":
            return WeaponModType.Melee
        elif slot == "Archgun":
            return WeaponModType.Archgun
        else:
            return WeaponModType.Misc


class RivenDisposition(BaseModel):
    disposition: float = 0.5  # Default min value
    symbol: str = "●○○○○"


class Weapon(BaseModel):
    name: str
    url: str
    image: str | None = None
    riven_disposition: RivenDisposition
    mod_type: WeaponModType = WeaponModType.Misc
    mr: int | None
    weapon_type: str | None = None
    slot: str | None = None
