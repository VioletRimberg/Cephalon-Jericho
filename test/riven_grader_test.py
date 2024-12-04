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
        ("Acceltra", ["MS", "DMG", "FR"], ["-ZOOM"], 5),  # Perfect
        ("Acceltra", ["MS", "DMG"], ["-SC"], 4),          # Prestigious
        ("Acceltra", ["DMG", "FR"], ["-SC"], 3),          # Decent
        ("Acceltra", ["FR", "CD"], ["-MS"], 1),           # Unusable
    ],
)
def test_grade_riven(mock_provider, weapon, positives, negatives, expected):

    riven_grader = RivenGrader()

    # Grade the riven using the RivenGrader's grade_riven method
    result = riven_grader.grade_riven(weapon, positives, negatives)

    # Assert the result matches the expected grade
    assert result == expected, f"Expected {expected}, but got {result}"