from dataclasses import dataclass
from jinja2 import Environment
import csv
import httpx
from typing import List
from riven_provider import RivenProvider

class RivenGrader:
    def __init__(self) -> None:
        # Initialize the RivenProvider class inside the RivenGrader
        self.riven_provider = RivenProvider.from_gsheets()  # Create an instance of RivenProvider

    def grade_riven(self, weapon: str, stats: list) -> int:
        """Grade the riven based on its stats."""
        # Get the weapon stats from the provider
        weapon_stats = self.riven_provider.get_weapon_stats(weapon)

        # Extract best, desired, and negative stats from the weapon stats
        best_stats = weapon_stats.get("BEST STAT", [])
        desired_stats = weapon_stats.get("DESIRED STAT", [])
        harmless_negatives = weapon_stats.get("NEGATIVE STAT", [])
        
        # Grading logic (adjusted as per our earlier discussion)
        best_matches = [stat for stat in stats if stat in best_stats]
        desired_matches = [stat for stat in stats if stat in desired_stats]
        detrimental_negatives = [stat for stat in stats if stat not in harmless_negatives and stat not in best_stats and stat not in desired_stats]

        # Check for Perfect match
        if len(best_matches) == 4 and (not detrimental_negatives or (len(detrimental_negatives) == 1 and detrimental_negatives[0] in harmless_negatives)):
            return 5  # Perfect

        # Check for Prestigious match
        elif best_matches and len(desired_matches) == len(stats) - len(best_matches) and not detrimental_negatives:
            return 4  # Prestigious

        # Check for Decent match
        elif (len(best_matches) >= 1 or len(desired_matches) >= len(stats) / 2) and not detrimental_negatives:
            return 3  # Decent

        # Check for Neutral match
        elif not detrimental_negatives:
            return 2  # Neutral

        # If harmful negatives are present
        return 1  # Unusable