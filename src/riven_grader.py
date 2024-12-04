from dataclasses import dataclass
from jinja2 import Environment
import csv
import httpx
from typing import List
from riven_provider import RivenProvider

# Initialize RivenProvider
RIVEN_PROVIDER = RivenProvider()
RIVEN_PROVIDER.from_gsheets()

def get_harmful_negatives(best_stats: List[str], desired_stats: List[str]) -> List[str]:
    """
    Combines best and desired stats into a harmful negatives list.

    Args:
        best_stats (list[str]): Best stats for the weapon.
        desired_stats (list[str]): Desired stats for the weapon.

    Returns:
        list[str]: Generalized harmful negatives.
    """
    return list(set(best_stats + desired_stats))

def grade_riven(
    weapon: str,
    positives: List[str],
    negatives: List[str],
    best_stats: List[str],
    desired_stats: List[str],
    harmless_negatives: List[str]
) -> int:
    """
    Grades a riven based on weapon-specific criteria.

    Args:
        weapon (str): Weapon name.
        positives (list[str]): List of positive stats.
        negatives (list[str]): List of negative stats.
        best_stats (list[str]): Best stats for the weapon.
        desired_stats (list[str]): Desired stats for the weapon.
        harmless_negatives (list[str]): Harmless negatives for the weapon.

    Returns:
        int: Grade from 1 (Unusable) to 5 (Perfect).
    """
    harmful_negatives = get_harmful_negatives(best_stats, desired_stats)
    
    # Classify negatives
    detrimental_negatives = [neg for neg in negatives if neg in harmful_negatives]
    
    # Classify positives
    best_matches = [stat for stat in positives if stat in best_stats]
    desired_matches = [stat for stat in positives if stat in desired_stats and stat not in best_stats]
    
   # Check for Perfect match (all best stats with no harmful negatives)
    if len(best_matches) == 4 and (not detrimental_negatives or len(detrimental_negatives) == 1 and detrimental_negatives[0] in harmless_negatives):
        return 5  # Perfect

    # Check for Prestigious match (at least one best stat, and the rest desired, no harmful negatives)
    elif best_matches and len(positives) == len(best_matches) + len(desired_matches) and not detrimental_negatives:
        return 4  # Prestigious

    # Check for Decent match (at least half the stats desired or harmless negatives, or one best stat, no harmful negatives)
    elif (len(best_matches) >= 1 or len(desired_matches) >= len(positives) / 2) and not detrimental_negatives:
        return 3  # Decent

    # Check for Neutral match (No harmful negatives)
    elif not detrimental_negatives:
        return 2  # Neutral

    # If there are harmful negatives, return Unusable
    else:
        return 1  # Unusable