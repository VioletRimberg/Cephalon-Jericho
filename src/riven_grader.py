from dataclasses import dataclass
from jinja2 import Environment
import csv
import httpx
from typing import List


class RivenGrader:
    def grade_riven(
        self,
        stats: list,
        best_stats: list,
        desired_stats: list,
        harmless_negatives: list,
    ) -> int:
        """Grade the riven based on its stats."""

        if len(stats) < 2 or len(stats) > 4:
            return 0  # Invalid riven due to too few or too many stats

        # Classify stats
        best_matches = [stat for stat in stats if stat in best_stats]
        desired_matches = [stat for stat in stats if stat in desired_stats]
        negative_stats = [stat for stat in stats if stat.startswith("-")]

        harmful_negatives = [
            stat
            for stat in negative_stats
            if stat[1:] in best_stats or stat[1:] in desired_stats
        ]
        harmless_negatives_in_stats = [
            stat for stat in negative_stats if stat[1:] in harmless_negatives
        ]
        neutral_negatives = [
            stat
            for stat in negative_stats
            if stat[1:] not in best_stats
            and stat[1:] not in desired_stats
            and stat[1:] not in harmless_negatives
        ]

        # 5 = Perfect: At least one best stat, no harmful negatives, and at least one harmless negative
        if (
            len(best_matches) >= 1
            and len(harmless_negatives_in_stats) == 1
            and len(desired_matches) == len(stats) - 1 - len(best_matches)
        ):
            return 5  # Perfect if at least one best stat, no harmful negatives, and one harmless negative

        # 4 = Prestigious: All desired stats, or a combination of best and desired stats, may have harmless or neutral negative
        if (
            len(best_matches) + len(desired_matches) == len(stats)
            and len(harmful_negatives) == 0
        ):
            return 4  # Prestigious if all desired stats with no harmful negative

        if len(best_matches) + len(desired_matches) > 0 and len(harmful_negatives) == 0:
            if len(stats) == len(best_matches) + len(desired_matches) + len(
                harmless_negatives_in_stats
            ) + len(neutral_negatives):
                return 4  # Prestigious if combination of best and desired stats with harmless/neutral negatives

        # 3 = Decent: At least one best or desired stat, the rest neutral or harmless negative, or no negative
        if (
            len(best_matches) == 1
            or len(desired_matches) + len(harmless_negatives_in_stats) >= len(stats) / 2
        ):
            if len(harmful_negatives) == 0:
                return 3  # Decent

        # 2 = Neutral: No best or desired stats, but no harmful negative
        if len(harmful_negatives) == 0:
            return 2  # Neutral

        # 1 = Unusable: Harmful negative present
        return 1  # Unusable
