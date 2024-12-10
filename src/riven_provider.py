from dataclasses import dataclass
from jinja2 import Environment
import csv
import httpx
from typing import List


class RivenProvider:
    def __init__(self) -> None:
        self.base_url = "https://docs.google.com/spreadsheets/d/1zbaeJBuBn44cbVKzJins_E3hTDpnmvOk8heYN-G8yy8/export?format=csv&gid="
        self.sheets = {
            "Primary": "0",
            "Secondary": "1505239276",
            "Melee": "1413904270",
            "Archgun": "289737427",
            "Robotic": "965095749",
        }
        self.normalized_data = []

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
            negative_stats_col = (
                headers.index("NEGATIVE STATS:")
                if "NEGATIVE STATS:" in headers
                else None
            )

        except ValueError as e:
            raise Exception(f"Missing expected columns in sheet {sheet_name}: {e}")

        # Process all rows after the header
        for row in data[1:]:
            weapon = row[weapon_col]
            positive_stats = row[best_stats_col]
            negative_stats = []  # Default to empty list if no negative stats column is found

            if negative_stats_col is not None:
                negative_stats = (
                    row[negative_stats_col].split("/")
                    if row[negative_stats_col]
                    else []
                )

            # Get unique stats
            best_stats, desired_stats, _ = self.extract_best_and_desired_stats(
                positive_stats
            )

            # Combine all extracted data into a dictionary
            normalized_row = {
                "SHEET": sheet_name,
                "WEAPON": weapon,
                "BEST STATS": best_stats,
                "DESIRED STATS": desired_stats,
                "NEGATIVE STATS": negative_stats,
            }

            # Add to the combined normalized data
            self.normalized_data.append(normalized_row)

    def from_gsheets(self):
        """
        Download and normalize all sheets from the Google Sheets URL.
        """
        for sheet_name, gid in self.sheets.items():
            url = f"{self.base_url}{gid}"

            # Fetch the sheet
            response = httpx.get(url, follow_redirects=True)
            if response.status_code != 200:
                raise Exception(
                    f"Failed to fetch CSV data for {sheet_name}: {response.status_code}"
                )

            # Save the sheet locally
            csv_file = f"{sheet_name}.csv"
            with open(csv_file, "w", newline="", encoding="utf-8") as file:
                file.write(response.text)

            # Normalize the sheet
            self.normalize_sheet(sheet_name, csv_file)

        # Write combined CSV
        with open(
            "combined_normalized_rivens.csv", "w", newline="", encoding="utf-8"
        ) as outfile:
            writer = csv.writer(outfile)
            writer.writerow(
                [
                    "SHEET",
                    "WEAPON",
                    "BEST STAT",
                    "BEST STAT",
                    "BEST STAT",
                    "DESIRED STAT",
                    "DESIRED STAT",
                    "DESIRED STAT",
                    "DESIRED STAT",
                    "NEGATIVE STAT",
                ]
            )  # Header row
            writer.writerows(self.normalized_data)

        print("Combined and normalized CSV created: combined_normalized_rivens.csv")
        print(
            f"Normalized data: {self.normalized_data[:5]}"
        )  # Print first 5 rows for debugging

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
