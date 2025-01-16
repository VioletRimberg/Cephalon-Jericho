import csv
import httpx
from utils.http import HardenedHttpClient
from model.rivens import RivenEffect
from pathlib import Path
import asyncio
import logging
from pydantic import BaseModel
from typing import Optional


class WantedRivenStats(BaseModel):
    best: Optional[list[RivenEffect]]
    wanted: Optional[list[RivenEffect]]
    wanted_negatives: Optional[list[RivenEffect]]


class RivenRecommendations(BaseModel):
    weapon: str
    comment: Optional[str]
    stats: list[WantedRivenStats]


class RivenProvider:
    def __init__(self, path: str = "./riven_data") -> None:
        self.base_url = "https://docs.google.com/spreadsheets/d/1zbaeJBuBn44cbVKzJins_E3hTDpnmvOk8heYN-G8yy8/export?format=csv&gid="
        self.sheets = {
            "Primary": "0",
            "Secondary": "1505239276",
            "Melee": "1413904270",
            "Archgun": "289737427",
            "Robotic": "965095749",
        }
        self.normalized_data = {}
        self.client = HardenedHttpClient(httpx.AsyncClient(follow_redirects=True))
        self.directory = Path(path)
        if not self.directory.exists():
            self.directory.mkdir(parents=True, exist_ok=True)

    def extract_best_and_desired_stats(self, cell: str):
        """
        Extract best, desired, and negative stats from a cell string while ensuring no duplicates
        and proper categorization.
        """
        best_stats = set()
        desired_stats = set()
        negative_stats = set()

        # Split the input by "or" to process multiple clauses
        options = cell.split(" or ")

        for option in options:
            # Split by space to separate groups of stats
            stats = option.split(" ")

            # The first group will be the "best" stats
            for stat in stats[0].split("/"):  # Split by slash if necessary
                stat = stat.strip()
                if stat.startswith(
                    "-"
                ):  # If the stat starts with "-", it's a negative stat
                    negative_stats.add(
                        stat[1:].strip()
                    )  # Add to negatives without the "-"
                else:
                    best_stats.add(stat)  # Otherwise, add to best stats

            # All subsequent groups are considered "desired" stats
            for stat_group in stats[1:]:
                for stat in stat_group.split("/"):  # Split by slash if necessary
                    stat = stat.strip()
                    if stat.startswith("-"):  # Handle negative stats here as well
                        negative_stats.add(stat[1:].strip())
                    elif stat not in best_stats:  # Avoid duplicates
                        desired_stats.add(stat)

        # Return lists for consistency
        return list(best_stats), list(desired_stats), list(negative_stats)

    def parse_stats(self, raw_stats: str) -> Optional[list[RivenEffect]]:
        if raw_stats == "":
            return None

        stats = []
        for stat in raw_stats.split("/"):
            try:
                stat = stat.strip()
                if stat.startswith("-"):
                    stat = stat[1:]
                if stat == "ELEMENT":
                    stats.append(RivenEffect.ELEC)
                    stats.append(RivenEffect.TOX)
                    stats.append(RivenEffect.HEAT)
                    stats.append(RivenEffect.COLD)
                elif stat == "RECOIL":
                    stats.append(RivenEffect.REC)
                elif stat == "AS":
                    stats.append(RivenEffect.FR)
                else:
                    stats.append(RivenEffect.try_parse(stat))
            except ValueError:
                logging.error(f"Failed to parse stat: {stat}")
        return stats if len(stats) > 0 else None

    def normalize_sheet(self, sheet_name: str, input_file: str):
        """
        Normalize the given sheet, ensuring rows are consistent and extracting best stats.
        This function dynamically adjusts to column positions based on the header row.
        """
        with open(input_file, "r", encoding="utf-8") as infile:
            reader = csv.reader(infile)
            data = list(reader)

        # The first row should contain headers, so we inspect it
        headers = data[0]
        try:
            # Dynamically find the column indices for each important field
            weapon_col = headers.index(
                "WEAPON"
            )  # Adjust to correct header name if needed
            best_stats_col = headers.index("POSITIVE STATS:")  # Adjust as needed
            negative_stats_col = headers.index("NEGATIVE STATS:")
            comment_col = headers.index("Notes:")

        except ValueError as e:
            raise Exception(f"Missing expected columns in sheet {sheet_name}: {e}")

        # Process all rows after the header
        for row in data[1:]:
            weapon = row[weapon_col].upper()
            raw_positive_stats = row[best_stats_col].upper()
            raw_negative_stats = row[
                negative_stats_col
            ].upper()  # Default to empty list if no negative stats column is found

            comment = row[comment_col]
            comment = comment if comment != "" else None

            negatives = self.parse_stats(raw_negative_stats)

            parsed_stats = []
            for positive_slices in raw_positive_stats.split(" OR "):
                try:
                    splits = positive_slices.split(" ")
                    raw_best = "/".join(splits[:-1])
                    raw_desired = splits[-1]
                    best = self.parse_stats(raw_best)
                    desired = self.parse_stats(raw_desired)

                    parsed_stats.append(
                        WantedRivenStats(
                            best=best, wanted=desired, wanted_negatives=negatives
                        )
                    )
                except Exception as e:
                    logging.error(f"Failed to parse stats for {weapon}: {e}")
                    continue

            self.normalized_data[weapon] = RivenRecommendations(
                weapon=weapon, comment=comment, stats=parsed_stats
            )

    async def from_gsheets(self, force_download: bool = False):
        """
        Download and normalize all sheets from the Google Sheets URL.
        """

        async def download_sheet(sheet_name, gid) -> Path:
            """
            Download the sheet with the given name and GID.
            Supports local caching to avoid redundant downloads.
            """
            file_path = self.directory / f"{sheet_name}.csv"
            if file_path.exists() and not force_download:
                logging.info(f"Skipping download of {sheet_name}.csv")
                return file_path
            url = f"{self.base_url}{gid}"
            response = await self.client.get(url)
            response.raise_for_status()
            with open(file_path, "w", newline="", encoding="utf-8") as file:
                file.write(response.text)
            return file_path

        tasks = [
            download_sheet(sheet_name, gid) for sheet_name, gid in self.sheets.items()
        ]
        paths = await asyncio.gather(*tasks)

        for path in paths:
            sheet_name = path.stem
            self.normalize_sheet(sheet_name, path)

        # with open(
        #     "combined_normalized_rivens.csv", "w", newline="", encoding="utf-8"
        # ) as outfile:
        #     writer = csv.writer(outfile)
        #     writer.writerow(
        #         [
        #             "SHEET",
        #             "WEAPON",
        #             "BEST STAT",
        #             "BEST STAT",
        #             "BEST STAT",
        #             "DESIRED STAT",
        #             "DESIRED STAT",
        #             "DESIRED STAT",
        #             "DESIRED STAT",
        #             "NEGATIVE STAT",
        #         ]
        #     )  # Header row
        #     writer.writerows(self.normalized_data)

        # print("Combined and normalized CSV created: combined_normalized_rivens.csv")
        # print(
        #     f"Normalized data: {self.normalized_data[:5]}"
        # )  # Print first 5 rows for debugging

    def get_weapon_stats(self, weapon: str):
        """
        Get the stats for a given weapon from the normalized data.
        Returns:
            dict: {
                "BEST STATS": List of best stats,
                "DESIRED STATS": List of desired stats,
                "NEGATIVE STATS": List of negative stats
            }
        """
        # Search for the weapon in the normalized data
        for entry in self.normalized_data:
            if entry["WEAPON"].lower() == weapon.lower():  # Case insensitive matching
                return {
                    "BEST STATS": entry["BEST STATS"],
                    "DESIRED STATS": entry["DESIRED STATS"],
                    "NEGATIVE STATS": entry["NEGATIVE STATS"],
                }

        # If weapon is not found, return empty lists for stats
        return {"BEST STATS": [], "DESIRED STATS": [], "NEGATIVE STATS": []}
