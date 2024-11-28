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
    best, desired, negative = provider.extract_best_and_desired_stats(cell_1)  # Call on instance
    assert best == ["MS"]
    assert desired == ["DMG","SC", "TOX"]
    assert negative == []

    # Test case: input with 'or'
    cell_2 = "MS DMG/SC/TOX or CD MS/TOX/CC/DMG"
    best, desired, negative = provider.extract_best_and_desired_stats(cell_2)  # Call on instance
    assert best == ["MS", "CD"]
    assert desired == ["DMG", "SC", "TOX", "MS", "TOX", "CC", "DMG"]
    assert negative == []

    # Test case: input with multiple 'or's
    cell_3 = "MS DMG/SC/TOX or CD MS/TOX/CC/DMG or FR CC/TOX"
    best, desired, negative = provider.extract_best_and_desired_stats(cell_3)  # Call on instance
    assert best == ["MS", "CD", "FR"]
    assert desired == ["DMG", "SC", "TOX", "MS", "TOX", "CC", "DMG", "CC", "TOX"]
    assert negative == []

# Test from_gsheets to ensure the sheets are fetched and normalized (mocked HTTP request)
def test_from_gsheets(monkeypatch):
    # Mock the HTTP response for the sheets
    def mock_httpx_get(url, *args, **kwargs):
        class MockResponse:
            def __init__(self):
                self.status_code = 200
                self.text = "Weapon,POSITIVE STATS:,NEGATIVE STATS:\nacceltra,CD MS/TOX/DMG/CC/FR,IMP/ZOOM\n"
        return MockResponse()

    monkeypatch.setattr(httpx, "get", mock_httpx_get)

    # Initialize the provider and fetch sheets
    provider = RivenProvider()
    provider.from_gsheets()

    # Ensure the normalized data has been populated after calling from_gsheets
    assert len(provider.normalized_data) > 0
    assert provider.normalized_data[0][1] == "acceltra"


if __name__ == "__main__":
    pytest.main()

