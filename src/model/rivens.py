from enum import Enum


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


class RivenEffects(str, Enum):
    CD = "Critical Damage"
    CC = "Critical Chance"
    DMG = "Damage"
    MS = "Multishot"
    FR = "Fire Rate"
    RLS = "Reload Speed"
    TOX = "Toxin"
    ELEC = "Electricity"
    HEAT = "Heat"
    COLD = "Cold"
    PUNC = "Puncture"
    SLASH = "Slash"
