import pytest
import pytest_asyncio
from src.sources import WarframeWiki, WeaponLookup


@pytest_asyncio.fixture(scope="session", autouse=True)
async def real_weapon_lookup():
    lookup = WeaponLookup()
    wiki = WarframeWiki(lookup)
    await wiki.refresh()
    return lookup


def test_is_constructable():
    lookup = WeaponLookup()
    assert lookup is not None


@pytest.mark.asyncio
async def test_fuzzy_search(real_weapon_lookup):
    matches = real_weapon_lookup.fuzzy_search("Bolt")
    assert len(matches) > 0
    assert any(match.display_name == "Boltor" for match in matches)


@pytest.mark.asyncio
async def test_relations(real_weapon_lookup):
    real_weapon_lookup.rebuild_weapon_relations()
    match = real_weapon_lookup["Boltor"]
    assert match.weapon_variants == ["boltor_prime", "telos_boltor"]

    match = real_weapon_lookup["Boltor Prime"]
    assert match.base_weapon == "boltor"

    match = real_weapon_lookup["Braton"]
    assert match.weapon_variants == ["braton_prime", "braton_vandal", "mk1-braton"]
