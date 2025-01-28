import pytest
from src.sources import WarframeWiki
import pytest_asyncio


@pytest_asyncio.fixture(scope="session", autouse=True)
async def real_wiki():
    wiki = WarframeWiki()
    await wiki.refresh()
    return wiki


def test_is_constructable():
    wiki = WarframeWiki()
    assert wiki is not None


@pytest.mark.asyncio
async def test_can_refresh(real_wiki):
    assert len(real_wiki.weapon_lookup) > 0


@pytest.mark.parametrize(
    "weapon_name",
    [
        "Ack & Brunt",
        "Boltor",
        "Mausolon",
        "Furis",
        "Glaive",
        "Cedo",
        "Dread",
        "Sweeper",
        "Deconstructor",
        "Tombfinger",  # Kitgun chamber
    ],
)
@pytest.mark.asyncio
async def test_can_get_weapon(weapon_name: str, real_wiki):
    weapon = await real_wiki.weapon(weapon_name)
    assert weapon is not None
    assert weapon.name == weapon_name


@pytest.mark.parametrize("weapon_name", ["cryophon_mk_iii"])
@pytest.mark.asyncio
async def test_can_get_railjack_weapon(weapon_name: str, real_wiki):
    weapon = await real_wiki.weapon(weapon_name)
    assert weapon is not None


@pytest.mark.asyncio
async def test_weapon_not_found(real_wiki):
    weapon = await real_wiki.weapon("Nonexistent Weapon")
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
