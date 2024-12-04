from dataclasses import dataclass
from jinja2 import Environment
import csv
import httpx
from typing import List
from .riven_provider import RivenProvider

class RivenGrader:
    def __init__(self) -> None:
        """Initialize the RivenGrader and automatically set up the RivenProvider."""
        self.riven_provider = RivenProvider()  # Initialize instance of RivenProvider
        self.riven_provider.from_gsheets()  # Call the instance method to load the data
    
    def grade_riven(self, weapon: str, stats: list, best_stats: list, desired_stats: list, harmless_negatives: list) -> int:
        """Grade the riven based on its stats."""
    
        # Check for invalid riven cases
        if len(stats) < 1 or len(stats) > 4:
            return 0  # Invalid riven due to too few or too many stats

        # Count negative stats (excluding harmless negatives)
        negative_stats = [stat for stat in stats if stat.startswith('-')]
        harmful_negatives = [
            stat for stat in negative_stats if stat[1:] in best_stats or stat[1:] in desired_stats
        ]
        # Harmless negatives: those that are in the harmless negatives list
        harmless_negatives_in_stats = [
            stat for stat in stats if stat.startswith('-') and stat[1:] in harmless_negatives
        ]
    
    # Count negative stats (excluding harmless negatives)
        negative_stats = [stat for stat in stats if stat.startswith('-')]
    
        # More than one negative stat (not counting harmless ones) means invalid
        if len(negative_stats) > 1 and len(harmless_negatives_in_stats) < len(negative_stats):
            return 0  # Invalid riven due to multiple negatives

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
            # If more than best stats, they must be desired stats and total stats must not exceed 4
            if len(stats) > len(best_matches):
                additional_stats = stats[len(best_matches):]
                # Check if additional stats are either desired or harmless negative
                if not all(stat in desired_stats or (stat.startswith('-') and stat[1:] in harmless_negatives) for stat in additional_stats):
                    return 1  # Invalid stats, not perfect
                if len(stats) > 4:
                    return 0  # Total stats exceed limit for Perfect

            # Perfect requires no harmful negatives at all
            if harmful_negatives:
                return 1  # Harmful negative, not perfect
        
            # Perfect can have one harmless negative
            if len(harmless_negatives_in_stats) > 1:
                return 0  # More than one harmless negative, not perfect
        
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

        # If harmful negatives are present and no other conditions match
        return 1  # Unusable