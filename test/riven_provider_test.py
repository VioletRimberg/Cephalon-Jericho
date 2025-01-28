import pytest
from src.sources import WarframeWiki, RivenRecommendationProvider


# Test RivenProvider initialization
def test_riven_provider_initialization():
    provider = RivenRecommendationProvider()

    # Ensure the object is constructed
    assert provider is not None
    # Ensure the sheets are properly initialized
    assert len(provider.sheets) == 5
    assert "Primary" in provider.sheets
    assert "Secondary" in provider.sheets
    assert "Melee" in provider.sheets
    assert "Archgun" in provider.sheets
    assert "Robotic" in provider.sheets


@pytest.mark.asyncio
async def test_refresh():
    # Initialize the provider and fetch sheets
    wiki = WarframeWiki()
    await wiki.refresh()
    weapon_lookup = wiki.weapon_lookup

    provider = RivenRecommendationProvider()
    await provider.refresh(weapon_lookup)

    # Ensure the normalized data has been populated after calling refresh
    assert len(weapon_lookup) > 0
    # Access the weapon name correctly using the key
    assert weapon_lookup["Acceltra"].riven_recommendations is not None
