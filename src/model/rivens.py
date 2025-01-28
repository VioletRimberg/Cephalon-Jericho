from enum import Enum
from pydantic import BaseModel
from .weapon import WeaponModType
from typing import NamedTuple, Optional


class RivenType(str, Enum):
    _2Pos0Neg = "2Pos0Neg"
    _2Pos1Neg = "2Pos1Neg"
    _3Pos0Neg = "3Pos0Neg"
    _3Pos1Neg = "3Pos1Neg"

    def bonus(self) -> float:
        match self:
            case RivenType._2Pos0Neg:
                return 0.99
            case RivenType._2Pos1Neg:
                return 1.2375
            case RivenType._3Pos0Neg:
                return 0.75
            case RivenType._3Pos1Neg:
                return 0.9375

    def malus(self) -> float:
        match self:
            case RivenType._2Pos1Neg:
                return -0.495
            case RivenType._3Pos1Neg:
                return -0.75
            case _:
                return 0


class RivenEffect(str, Enum):
    CD = "Critical Damage"
    CC = "Critical Chance"
    DMG = "Damage / Melee Damage"
    MS = "Multishot"
    FR = "Fire Rate / Attack Speed"
    RLS = "Reload Speed"
    TOX = "Toxin Damage"
    DTC = "Damage to Corpus"
    DTI = "Damage to Infested"
    DTG = "Damage to Grineer"
    PUNC = "Puncture"
    IMP = "Impact"
    MAG = "Magazine Capacity"
    REC = "Recoil"
    SC = "Status Chance"
    PT = "Punch Through"
    PFS = "Projectile Speed / Projectile Flight Speed"
    IC = "Initial Combo"
    EFF = "Heavy Attack Efficiency"
    SLIDE = "Critical Chance on Slide Attack"
    FIN = "Finisher Damage"
    ELEC = "Electricity Damage"
    SD = "Status Duration"

    # Additional abbreviations not in the original legend:
    ZOOM = "Zoom"
    RANGE = "Range"
    SLASH = "Slash Damage"
    HEAT = "Heat Damage"
    COLD = "Cold Damage"
    CDUR = "Combo Duration"
    CNCC = "Chance Not to Gain Combo Count"
    AMMO = "Ammo Maximum"
    ACCC = "Additional Combo Count Chance"

    @classmethod
    def try_parse(cls, value: str) -> "RivenEffect":
        upper_value = value.upper().strip()
        for effect in cls:
            if effect.name == upper_value:
                return effect
        raise ValueError(f"Invalid RivenEffect: {value}")

    def render(self, weapon_type: WeaponModType) -> str:
        """
        Render the effect as a string for the given weapon type
        """
        if self == RivenEffect.DMG:
            return "Melee Damage" if weapon_type == WeaponModType.Melee else "Damage"

        if self == RivenEffect.FR:
            return "Attack Speed" if weapon_type == WeaponModType.Melee else "Fire Rate"

        return self.value

    def get_stat(self, stat: float, is_negative: bool) -> float:
        """
        Apply inversion and nagative denominator to the stat
        """

        if self.is_inverted():
            stat = stat * -1

        if is_negative:
            stat = stat * -1

        return stat

    def is_inverted(self) -> bool:
        if self in [RivenEffect.REC]:
            return True
        return False

    def valid_on_mod_type(self, mod_type: WeaponModType) -> bool:
        return RIVEN_EFFECT_LOOKUP[self].values[mod_type] is not None

    def calculate_range(
        self,
        disposition: float,
        mod_type: WeaponModType,
        riven_type: RivenType,
        is_negative: bool,
    ) -> tuple[float, float]:
        base = RIVEN_EFFECT_LOOKUP[self].values[mod_type]
        if base is None:
            return ValueError(
                f"Stat `{self.value}` is not valid for weapon type `{mod_type.value}`"
            )

        if is_negative:
            base *= riven_type.malus()
        else:
            base *= riven_type.bonus()

        with_disposition = base * disposition

        if self.is_inverted():
            with_disposition = with_disposition * -1

        if with_disposition < 0:
            # Invert the range for negative stats
            return with_disposition * 1.1, with_disposition * 0.9
        else:
            return with_disposition * 0.9, with_disposition * 1.1


class RivenAttribute(BaseModel):
    effect: RivenEffect
    prefix: str
    suffix: str
    values: dict[WeaponModType, Optional[float]]


class RivenStat(NamedTuple):
    effect: RivenEffect
    value: float

    def __str__(self) -> str:
        return f"{self.effect.value}: {self.value}"


class Riven(BaseModel):
    name: str
    weapon: str
    positives: list[RivenStat]
    negatives: list[RivenStat]

    @property
    def all_stats(self) -> list[tuple[RivenStat, bool]]:
        return list(
            zip(
                self.positives + self.negatives,
                [True] * len(self.positives) + [False] * len(self.negatives),
            )
        )

    @property
    def riven_type(self) -> RivenType:
        """
        Try to determine the type of riven based on the number of positives and negatives.
        """
        match len(self.positives):
            case 2:
                match len(self.negatives):
                    case 0:
                        return RivenType._2Pos0Neg
                    case 1:
                        return RivenType._2Pos1Neg
            case 3:
                match len(self.negatives):
                    case 0:
                        return RivenType._3Pos0Neg
                    case 1:
                        return RivenType._3Pos1Neg

        raise ValueError(
            "Riven with `{}` positives and `{}` negatives can't exist!".format(
                len(self.positives), len(self.negatives)
            )
        )


RIVEN_EFFECT_LOOKUP: dict[RivenEffect, RivenAttribute] = {
    # 1) Zoom
    RivenEffect.ZOOM: RivenAttribute(
        effect=RivenEffect.ZOOM,
        prefix="Hera",
        suffix="Lis",
        values={
            WeaponModType.Rifle: 59.99,
            WeaponModType.Shotgun: None,
            WeaponModType.Pistol: 80.1,
            WeaponModType.Archgun: 59.99,
            WeaponModType.Melee: None,
        },
    ),
    # 2) Status Duration
    RivenEffect.SD: RivenAttribute(
        effect=RivenEffect.SD,
        prefix="Deci",
        suffix="Des",
        values={
            WeaponModType.Rifle: 99.99,
            WeaponModType.Shotgun: 99.0,
            WeaponModType.Pistol: 99.99,
            WeaponModType.Archgun: 99.99,
            WeaponModType.Melee: 99.0,
        },
    ),
    # 3) Status Chance
    RivenEffect.SC: RivenAttribute(
        effect=RivenEffect.SC,
        prefix="Hexa",
        suffix="Dex",
        values={
            WeaponModType.Rifle: 90.0,
            WeaponModType.Shotgun: 90.0,
            WeaponModType.Pistol: 90.0,
            WeaponModType.Archgun: 60.3,
            WeaponModType.Melee: 90.0,
        },
    ),
    # 4) Reload Speed
    RivenEffect.RLS: RivenAttribute(
        effect=RivenEffect.RLS,
        prefix="Feva",
        suffix="Tak",
        values={
            WeaponModType.Rifle: 50.0,
            WeaponModType.Shotgun: 49.45,
            WeaponModType.Pistol: 50.0,
            WeaponModType.Archgun: 99.9,
            WeaponModType.Melee: None,
        },
    ),
    # 5) Recoil
    RivenEffect.REC: RivenAttribute(
        effect=RivenEffect.REC,
        prefix="Zeti",
        suffix="Mag",
        values={
            WeaponModType.Rifle: 90.0,
            WeaponModType.Shotgun: 90.0,
            WeaponModType.Pistol: 90.0,
            WeaponModType.Archgun: 90.0,
            WeaponModType.Melee: None,
        },
    ),
    # 6) Range (melee only)
    RivenEffect.RANGE: RivenAttribute(
        effect=RivenEffect.RANGE,
        prefix="Locti",
        suffix="Tor",
        values={
            WeaponModType.Rifle: None,
            WeaponModType.Shotgun: None,
            WeaponModType.Pistol: None,
            WeaponModType.Archgun: None,
            WeaponModType.Melee: 1.94,
        },
    ),
    # 7) Punch Through
    RivenEffect.PT: RivenAttribute(
        effect=RivenEffect.PT,
        prefix="Lexi",
        suffix="Nok",
        values={
            WeaponModType.Rifle: 2.7,
            WeaponModType.Shotgun: 2.7,
            WeaponModType.Pistol: 2.7,
            WeaponModType.Archgun: 2.7,
            WeaponModType.Melee: None,
        },
    ),
    # 8) Projectile Speed
    RivenEffect.PFS: RivenAttribute(
        effect=RivenEffect.PFS,
        prefix="Conci",
        suffix="Nak",
        values={
            WeaponModType.Rifle: 90.0,
            WeaponModType.Shotgun: 89.1,
            WeaponModType.Pistol: 90.0,
            WeaponModType.Archgun: None,
            WeaponModType.Melee: None,
        },
    ),
    # 9) Multishot
    RivenEffect.MS: RivenAttribute(
        effect=RivenEffect.MS,
        prefix="Sati",
        suffix="Can",
        values={
            WeaponModType.Rifle: 90.0,
            WeaponModType.Shotgun: 119.7,
            WeaponModType.Pistol: 119.7,
            WeaponModType.Archgun: 60.3,
            WeaponModType.Melee: None,
        },
    ),
    # 10) Damage / Melee Damage (also referred to as Base Damage in the table)
    RivenEffect.DMG: RivenAttribute(
        effect=RivenEffect.DMG,
        prefix="Visi",
        suffix="Ata",
        values={
            WeaponModType.Rifle: 165.0,
            WeaponModType.Shotgun: 164.7,
            WeaponModType.Pistol: 219.6,
            WeaponModType.Archgun: 99.9,
            WeaponModType.Melee: 164.7,
        },
    ),
    # 11) Magazine Capacity
    RivenEffect.MAG: RivenAttribute(
        effect=RivenEffect.MAG,
        prefix="Arma",
        suffix="Tin",
        values={
            WeaponModType.Rifle: 50.0,
            WeaponModType.Shotgun: 50.0,
            WeaponModType.Pistol: 50.0,
            WeaponModType.Archgun: 60.3,
            WeaponModType.Melee: None,
        },
    ),
    # 12) Initial Combo
    RivenEffect.IC: RivenAttribute(
        effect=RivenEffect.IC,
        prefix="Para",
        suffix="Um",
        values={
            WeaponModType.Rifle: None,
            WeaponModType.Shotgun: None,
            WeaponModType.Pistol: None,
            WeaponModType.Archgun: None,
            WeaponModType.Melee: 24.5,
        },
    ),
    # 13) Heavy Attack Efficiency
    RivenEffect.EFF: RivenAttribute(
        effect=RivenEffect.EFF,
        prefix="Forti",
        suffix="Us",
        values={
            WeaponModType.Rifle: None,
            WeaponModType.Shotgun: None,
            WeaponModType.Pistol: None,
            WeaponModType.Archgun: None,
            WeaponModType.Melee: 73.44,
        },
    ),
    # 14) Fire Rate / Attack Speed
    RivenEffect.FR: RivenAttribute(
        effect=RivenEffect.FR,
        prefix="Croni",
        suffix="Dra",
        values={
            WeaponModType.Rifle: 60.03,
            WeaponModType.Shotgun: 89.1,
            WeaponModType.Pistol: 74.7,
            WeaponModType.Archgun: 60.03,
            WeaponModType.Melee: 54.9,
        },
    ),
    # 15) Finisher Damage
    RivenEffect.FIN: RivenAttribute(
        effect=RivenEffect.FIN,
        prefix="Exi",
        suffix="Cta",
        values={
            WeaponModType.Rifle: None,
            WeaponModType.Shotgun: None,
            WeaponModType.Pistol: None,
            WeaponModType.Archgun: None,
            WeaponModType.Melee: 119.7,
        },
    ),
    # 16) Toxin Damage
    RivenEffect.TOX: RivenAttribute(
        effect=RivenEffect.TOX,
        prefix="Toxi",
        suffix="Tox",
        values={
            WeaponModType.Rifle: 90.0,
            WeaponModType.Shotgun: 90.0,
            WeaponModType.Pistol: 90.0,
            WeaponModType.Archgun: 119.7,
            WeaponModType.Melee: 90.0,
        },
    ),
    # 17) Slash Damage
    RivenEffect.SLASH: RivenAttribute(
        effect=RivenEffect.SLASH,
        prefix="Sci",
        suffix="Sus",
        values={
            WeaponModType.Rifle: 119.97,
            WeaponModType.Shotgun: 119.97,
            WeaponModType.Pistol: 119.97,
            WeaponModType.Archgun: 90.0,
            WeaponModType.Melee: 119.7,
        },
    ),
    # 18) Puncture
    RivenEffect.PUNC: RivenAttribute(
        effect=RivenEffect.PUNC,
        prefix="Insi",
        suffix="Cak",
        values={
            WeaponModType.Rifle: 119.97,
            WeaponModType.Shotgun: 119.97,
            WeaponModType.Pistol: 119.97,
            WeaponModType.Archgun: 90.0,
            WeaponModType.Melee: 119.7,
        },
    ),
    # 19) Impact
    RivenEffect.IMP: RivenAttribute(
        effect=RivenEffect.IMP,
        prefix="Magna",
        suffix="Ton",
        values={
            WeaponModType.Rifle: 119.97,
            WeaponModType.Shotgun: 119.97,
            WeaponModType.Pistol: 119.97,
            WeaponModType.Archgun: 90.0,
            WeaponModType.Melee: 119.7,
        },
    ),
    # 20) Heat Damage
    RivenEffect.HEAT: RivenAttribute(
        effect=RivenEffect.HEAT,
        prefix="Igni",
        suffix="Pha",
        values={
            WeaponModType.Rifle: 90.0,
            WeaponModType.Shotgun: 90.0,
            WeaponModType.Pistol: 90.0,
            WeaponModType.Archgun: 119.7,
            WeaponModType.Melee: 90.0,
        },
    ),
    # 21) Electricity Damage
    RivenEffect.ELEC: RivenAttribute(
        effect=RivenEffect.ELEC,
        prefix="Vexi",
        suffix="Tio",
        values={
            WeaponModType.Rifle: 90.0,
            WeaponModType.Shotgun: 90.0,
            WeaponModType.Pistol: 90.0,
            WeaponModType.Archgun: 119.7,
            WeaponModType.Melee: 90.0,
        },
    ),
    # 22) Cold Damage
    RivenEffect.COLD: RivenAttribute(
        effect=RivenEffect.COLD,
        prefix="Geli",
        suffix="Do",
        values={
            WeaponModType.Rifle: 90.0,
            WeaponModType.Shotgun: 90.0,
            WeaponModType.Pistol: 90.0,
            WeaponModType.Archgun: 119.7,
            WeaponModType.Melee: 90.0,
        },
    ),
    # 23) Damage to Infested
    RivenEffect.DTI: RivenAttribute(
        effect=RivenEffect.DTI,
        prefix="Pura",
        suffix="Ada",
        values={
            WeaponModType.Rifle: 45.0,
            WeaponModType.Shotgun: 45.0,
            WeaponModType.Pistol: 45.0,
            WeaponModType.Archgun: 45.0,
            WeaponModType.Melee: 45.0,
        },
    ),
    # 24) Damage to Grineer
    RivenEffect.DTG: RivenAttribute(
        effect=RivenEffect.DTG,
        prefix="Argi",
        suffix="Con",
        values={
            WeaponModType.Rifle: 45.0,
            WeaponModType.Shotgun: 45.0,
            WeaponModType.Pistol: 45.0,
            WeaponModType.Archgun: 45.0,
            WeaponModType.Melee: 45.0,
        },
    ),
    # 25) Damage to Corpus
    RivenEffect.DTC: RivenAttribute(
        effect=RivenEffect.DTC,
        prefix="Manti",
        suffix="Tron",
        values={
            WeaponModType.Rifle: 45.0,
            WeaponModType.Shotgun: 45.0,
            WeaponModType.Pistol: 45.0,
            WeaponModType.Archgun: 45.0,
            WeaponModType.Melee: 45.0,
        },
    ),
    # 26) Critical Damage
    RivenEffect.CD: RivenAttribute(
        effect=RivenEffect.CD,
        prefix="Acri",
        suffix="Tis",
        values={
            WeaponModType.Rifle: 120.0,
            WeaponModType.Shotgun: 90.0,
            WeaponModType.Pistol: 90.0,
            WeaponModType.Archgun: 80.1,
            WeaponModType.Melee: 90.0,
        },
    ),
    # 27) Critical Chance on Slide Attack
    RivenEffect.SLIDE: RivenAttribute(
        effect=RivenEffect.SLIDE,
        prefix="Pleci",
        suffix="Nent",
        values={
            WeaponModType.Rifle: None,
            WeaponModType.Shotgun: None,
            WeaponModType.Pistol: None,
            WeaponModType.Archgun: None,
            WeaponModType.Melee: 120.0,
        },
    ),
    # 28) Critical Chance
    RivenEffect.CC: RivenAttribute(
        effect=RivenEffect.CC,
        prefix="Crita",
        suffix="Cron",
        values={
            WeaponModType.Rifle: 149.99,
            WeaponModType.Shotgun: 90.0,
            WeaponModType.Pistol: 149.99,
            WeaponModType.Archgun: 99.9,
            WeaponModType.Melee: 180.0,
        },
    ),
    # 29) Combo Duration
    RivenEffect.CDUR: RivenAttribute(
        effect=RivenEffect.CDUR,
        prefix="Tempi",
        suffix="Nem",
        values={
            WeaponModType.Rifle: None,
            WeaponModType.Shotgun: None,
            WeaponModType.Pistol: None,
            WeaponModType.Archgun: None,
            WeaponModType.Melee: 8.1,
        },
    ),
    # 30) Chance Not to Gain Combo Count
    RivenEffect.CNCC: RivenAttribute(
        effect=RivenEffect.CNCC,
        prefix="?",
        suffix="?",
        values={
            WeaponModType.Rifle: None,
            WeaponModType.Shotgun: None,
            WeaponModType.Pistol: None,
            WeaponModType.Archgun: None,
            WeaponModType.Melee: 104.85,
        },
    ),
    # 31) Ammo Maximum
    RivenEffect.AMMO: RivenAttribute(
        effect=RivenEffect.AMMO,
        prefix="Ampi",
        suffix="Bin",
        values={
            WeaponModType.Rifle: 49.95,
            WeaponModType.Shotgun: 90.0,
            WeaponModType.Pistol: 90.0,
            WeaponModType.Archgun: 99.9,
            WeaponModType.Melee: None,
        },
    ),
    # 32) Additional Combo Count Chance
    RivenEffect.ACCC: RivenAttribute(
        effect=RivenEffect.ACCC,
        prefix="Laci",
        suffix="Nus",
        values={
            WeaponModType.Rifle: None,
            WeaponModType.Shotgun: None,
            WeaponModType.Pistol: None,
            WeaponModType.Archgun: None,
            WeaponModType.Melee: 58.77,
        },
    ),
}
