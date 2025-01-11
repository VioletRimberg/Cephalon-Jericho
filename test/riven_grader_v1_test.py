import pytest
from src.riven_grader_v1 import RivenGrader


# Parameterized test cases
@pytest.mark.parametrize(
    "positives, negatives, expected",
    [
        (["MS", "CD", "FR"], ["-ZOOM"], 5),  # Perfect
        (["MS", "CD", "FR"], ["-SC"], 4),  # Prestigious
        (["DMG", "MS", "TOX"], ["-SC"], 3),  # Decent
        (["COLD", "TOX"], ["-SC"], 2),  # Neutral
        (["FR", "CD"], ["-MS"], 1),  # Unusable
    ],
)
def test_grade_riven(positives, negatives, expected):
    # Combine positives and negatives into a single stats list
    stats = positives + negatives

    # Mock the RivenProvider methods to return appropriate data
    best_stats = ["CD"]
    desired_stats = ["DMG", "FR", "MS"]
    harmless_negatives = ["ZOOM"]  # Keep harmless as "-ZOOM"

    # Initialize the RivenGrader
    riven_grader = RivenGrader()

    # Grade the riven
    result = riven_grader.grade_riven(
        stats, best_stats, desired_stats, harmless_negatives
    )

    # Assert the result matches the expected grade
    assert result == expected
