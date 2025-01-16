import pytest
from src.riven_grader import RivenGrader
from src.model import Riven, RivenEffect
from src.sources import WarframeWiki


def test_is_constructable():
    wiki = WarframeWiki()
    riven_grader = RivenGrader(wiki)
    assert riven_grader is not None


@pytest.mark.parametrize(
    "riven",
    [
        Riven(
            name="Laetum",
            weapon="Laetum",
            positives=[(RivenEffect.MS, 63.8), (RivenEffect.DMG, 104.7)],
            negatives=[],
        ),  # 2 positives
        Riven(
            name="Torid",
            weapon="Torid",
            positives=[
                (RivenEffect.ELEC, 92.2),
                (RivenEffect.MS, 86.1),
                (RivenEffect.PFS, 90.8),
            ],
            negatives=[],
        ),  # 3 positives
        Riven(
            name="Nami Solo",
            weapon="Nami Solo",
            positives=[(RivenEffect.SC, 147.5), (RivenEffect.FR, 89.6)],
            negatives=[(RivenEffect.SLASH, -83.5)],
        ),  # 2 positives 1 negative
        Riven(
            name="Strun",
            weapon="Strun",
            positives=[
                (RivenEffect.DMG, 214.9),
                (RivenEffect.CC, 120.3),
                (RivenEffect.RLS, 67.1),
            ],
            negatives=[(RivenEffect.SC, -89.7)],
        ),  # 3 positives 1 negative
        Riven(
            name="Strun",
            weapon="Strun",
            positives=[(RivenEffect.ELEC, 167.4), (RivenEffect.MS, 220.7)],
            negatives=[(RivenEffect.REC, 63.9)],
        ),  # neg recoil
        Riven(
            name="Dual Toxocyst",
            weapon="Dual Toxocyst",
            positives=[
                (RivenEffect.REC, -93.1),
                (RivenEffect.CD, 84.1),
                (RivenEffect.SC, 97.2),
            ],
            negatives=[],
        ),  # pos recoil
    ],
)
@pytest.mark.asyncio
async def test_can_valdiate_valid_riven(riven):
    wiki = WarframeWiki()
    await wiki.refresh()
    riven_grader = RivenGrader(wiki)
    result, error = await riven_grader.valdiate(riven)
    assert result
