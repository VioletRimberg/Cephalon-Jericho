import pytest
import httpx
from src.riven_provider import RivenProvider


# Test RivenProvider initialization
def test_riven_provider_initialization():
    provider = RivenProvider()

    # Ensure the object is constructed
    assert provider is not None

    # Ensure the sheets are properly initialized
    assert len(provider.sheets) == 5
    assert "Primary" in provider.sheets
    assert "Secondary" in provider.sheets
    assert "Melee" in provider.sheets
    assert "Archgun" in provider.sheets
    assert "Robotic" in provider.sheets

    # Ensure the normalized data is initially empty
    assert len(provider.normalized_data) == 0


# Test extracting stats from a sample cell
def test_extract_best_and_desired_stats():
    provider = RivenProvider()

    # Test case: normal input without 'or'
    cell_1 = "MS DMG/SC/TOX"
    best, desired, negative = provider.extract_best_and_desired_stats(
        cell_1
    )  # Call on instance
    assert set(best) == {"MS"}
    assert set(desired) == {"DMG", "SC", "TOX"}
    assert set(negative) == set()

    # Test case: input with 'or'
    cell_2 = "MS DMG/SC/TOX or CD MS/TOX/CC/DMG"
    best, desired, negative = provider.extract_best_and_desired_stats(
        cell_2
    )  # Call on instance
    assert set(best) == {"MS", "CD"}
    assert set(desired) == {"DMG", "SC", "TOX", "CC"}
    assert set(negative) == set()

    # Test case: input with multiple 'or's
    cell_3 = "MS DMG/SC/TOX or CD MS/TOX/CC/DMG or FR CC/TOX"
    best, desired, negative = provider.extract_best_and_desired_stats(
        cell_3
    )  # Call on instance
    assert set(best) == {"MS", "CD", "FR"}
    assert set(desired) == {"DMG", "SC", "TOX", "CC"}
    assert set(negative) == set()


@pytest.mark.asyncio
async def test_from_gsheets():
    # Initialize the provider and fetch sheets
    provider = RivenProvider()
    await provider.from_gsheets()

    # Ensure the normalized data has been populated after calling from_gsheets
    assert len(provider.normalized_data) > 0
    # Access the weapon name correctly using the key
    assert "ACCELTRA" in provider.normalized_data


if __name__ == "__main__":
    pytest.main()
