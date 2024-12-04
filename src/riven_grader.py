from dataclasses import dataclass
from jinja2 import Environment
import csv
import httpx
from typing import List
from riven_provider import RivenProvider

class RivenGrader:
    def __init__(self) -> None:
        """Initialize the RivenGrader and automatically set up the RivenProvider."""
        self.riven_provider = RivenProvider()  # Initialize instance of RivenProvider
        self.riven_provider.from_gsheets()  # Call the instance method to load the data
    
    def grade_riven(self, weapon: str, stats: list, best_stats: list, desired_stats: list, harmless_negatives: list) -> int:
        """Grade the riven based on its stats."""
        
        # Extract the relevant stats
        best_matches = [stat for stat in stats if stat in best_stats]
        desired_matches = [stat for stat in stats if stat in desired_stats]
        
        # Harmful negatives: those that are negative versions of best or desired stats
        harmful_negatives = [
            stat for stat in stats if stat.startswith('-') and (stat[1:] in best_stats or stat[1:] in desired_stats)
        ]
        
        # Harmless negatives: those that are in the harmless negatives list
        harmless_negatives_in_stats = [
            stat for stat in stats if stat.startswith('-') and stat[1:] in harmless_negatives
        ]
        
        # Check for Perfect match
        if len(best_matches) == len(best_stats) and len(stats) <= 4:
        # Perfect can only have harmful negatives if they are harmless
            if not harmful_negatives or (len(harmful_negatives) == 1 and harmful_negatives[0] in harmless_negatives_in_stats):
                return 5  # Perfect
    
    # Check for Prestigious match
        elif (len(best_matches) >= 1 or len(desired_matches) == len(stats)) and not harmful_negatives:
        # Prestigious can have a harmless negative or any non-detrimental negative
            if harmless_negatives_in_stats or (len(desired_matches) + len(harmless_negatives_in_stats) >= 2):
                return 4  # Prestigious
    
        # Check for Decent match
        elif len(best_matches) == 1 or len(desired_matches) + len(harmless_negatives_in_stats) >= len(stats) / 2:
            # Decent cannot have any harmful negatives
            if not harmful_negatives:
                return 3  # Decent

        # Check for Neutral match
        elif not harmful_negatives:
            return 2  # Neutral

        # If harmful negatives are present
        return 1  # Unusable