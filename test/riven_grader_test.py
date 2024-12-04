import pytest
from src.riven_grader import grade_riven
from src.riven_provider import MockRivenProvider

# Fixture to provide a mock RivenProvider
@pytest.fixture
def mock_provider():
    return MockRivenProvider()

# Parameterized test cases
@pytest.mark.parametrize(
    "weapon, positives, negatives, expected",
    [
        ("Acceltra", ["MS", "DMG", "FR"], ["-ZOOM"], 5),  # Perfect
        ("Acceltra", ["MS", "DMG"], ["-SC"], 4),          # Prestigious
        ("Acceltra", ["DMG", "FR"], ["-SC"], 3),          # Decent
        ("Acceltra", ["FR", "CD"], ["-MS"], 1),           # Unusable
    ],
)
def test_grade_riven(mock_provider, weapon, positives, negatives, expected):
    # Get weapon stats from the provider
    stats = mock_provider.get_weapon_stats(weapon)
    best_stats = stats["best"]
    desired_stats = stats["desired"]
    harmless_negatives = stats["harmless_negatives"]
    
    # Grade the riven
    result = grade_riven(weapon, positives, negatives, best_stats, desired_stats, harmless_negatives)
    
    # Assert the result matches the expected grade
    assert result == expected, f"Expected {expected}, but got {result}."