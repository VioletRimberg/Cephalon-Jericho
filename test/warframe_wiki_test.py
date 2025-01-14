import pytest
from src.warframe_wiki import WarframeWiki


def test_is_constructable():
    wiki = WarframeWiki()
    assert wiki is not None


@pytest.mark.asyncio
async def test_can_refresh():
    wiki = WarframeWiki()
    await wiki.refresh()
    assert len(wiki.weapon_lookup) > 0


@pytest.mark.parametrize(
    "weapon_name", ["Ack & Brunt", "Boltor", "Mausolon", "Furis", "Glaive"]
)
@pytest.mark.asyncio
async def test_can_get_weapon(weapon_name: str):
    wiki = WarframeWiki()
    await wiki.refresh()
    weapon = await wiki.weapon(weapon_name)
    assert weapon is not None
    assert weapon.name == weapon_name


@pytest.mark.asyncio
async def test_weapon_not_found():
    wiki = WarframeWiki()
    await wiki.refresh()
    weapon = await wiki.weapon("Nonexistent Weapon")
    assert weapon is None


@pytest.mark.skip(reason="Takes too long to run")
@pytest.mark.asyncio
async def test_all_weapons():
    wiki = WarframeWiki()
    await wiki.refresh()
    matches = 0
    for weapon_name in wiki.weapon_lookup.keys():
        weapon = await wiki.weapon(weapon_name)
        assert weapon is not None
        match = wiki._clean_weapon_name(weapon.name).startswith(weapon_name)
        matches += int(match)
    print(f"Matched {matches} out of {len(wiki.weapon_lookup)} weapons")
