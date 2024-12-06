import pytest
from src.riven_grader import RivenGrader
from src.riven_provider import RivenProvider

# Fixture to provide a mock RivenProvider
@pytest.fixture
def mock_provider():
    # Return a mock provider instance
    return RivenProvider()

# Parameterized test cases
@pytest.mark.parametrize(
    "weapon, positives, negatives, expected",
    [
        ("Acceltra", ["MS", "CD", "FR"], ["-ZOOM"], 5),  # Perfect
        ("Acceltra", ["MS", "CD", "FR"], ["-SC"], 4),          # Prestigious
        ("Acceltra", ["DMG", "MS", "TOX"], ["-SC"], 3),          # Decent
        ("Acceltra", ["COLD", "TOX"], ["-SC"], 2),   # Neutral
        ("Acceltra", ["FR", "CD"], ["-MS"], 1),           # Unusable
    ],
)
def test_grade_riven(mock_provider, weapon, positives, negatives, expected):
    # Combine positives and negatives into a single stats list
    stats = positives + negatives

    # Mock the RivenProvider methods to return appropriate data
    mock_provider.get_best_stats = lambda weapon: ["CD"]
    mock_provider.get_desired_stats = lambda weapon: ["DMG", "FR", "MS"]
    mock_provider.get_harmless_negatives = lambda weapon: ["-ZOOM"]  # Keep harmless as "-ZOOM"

    # Fetch the required data from the mock provider
    best_stats = mock_provider.get_best_stats(weapon)
    desired_stats = mock_provider.get_desired_stats(weapon)
    harmless_negatives = mock_provider.get_harmless_negatives(weapon)

    # Initialize the RivenGrader
    riven_grader = RivenGrader()

    # Grade the riven
    result = riven_grader.grade_riven(weapon, stats, best_stats, desired_stats, harmless_negatives)

    # Assert the result matches the expected grade
    assert result == expected