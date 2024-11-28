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
     
        best_stats = []
        desired_stats = []
        negative_stats = []
        
        # First, split the string by "or" to handle alternative options
        options = cell.split(" or ")
        
        for option in options:
            # Split by space to separate individual stats
            stats = option.split(" ")
            
            # The first item will be the "best" stats (the ones separated by spaces)
            best_stats.extend(stats[0].split("/"))  # Split by slash if necessary
            
            # All subsequent stats are considered "desired" stats
            for stat in stats[1:]:
                desired_stats.extend(stat.split("/"))  # Split by slash if necessary

        return best_stats, desired_stats, negative_stats
    
    def normalize_sheet(self, sheet_name: str, input_file: str):
        """
        Normalize the given sheet, ensuring rows are consistent and extracting best stats.
        """
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            data = list(reader)

        # Skip header row (the first line)
        data = data[1:]

        # Normalize the sheet's data
        for row in data:
            weapon = row[0]  # Weapon name is the first column
            positive_stats = row[1]  # Positive stats column
            negative_stats = row[2] if len(row) > 2 else ""  # Negative stats column (may not exist in some rows)

            best_stats, desired_stats, negative_stats = self.extract_best_and_desired_stats(positive_stats)

            # Combine all extracted data into a new row
            normalized_row = [sheet_name, weapon] + best_stats + desired_stats + ["negative stat " + stat for stat in negative_stats]

            # Add to the combined normalized data
            self.normalized_data.append(normalized_row)

    def from_gsheets(self):
        """
        Download and normalize all sheets from the Google Sheets URL.
        """
        for sheet_name, gid in self.sheets.items():
            url = f"{self.base_url}{gid}"

            # Fetch the sheet
            response = httpx.get(url)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch CSV data for {sheet_name}: {response.status_code}")

            # Save the sheet locally
            csv_file = f"{sheet_name}.csv"
            with open(csv_file, "w", newline="", encoding="utf-8") as file:
                file.write(response.text)
            
            # Normalize the sheet
            self.normalize_sheet(sheet_name, csv_file)

        # Write combined CSV
        with open("combined_normalized_rivens.csv", "w", newline="", encoding="utf-8") as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["SHEET", "WEAPON", "BEST STAT", "BEST STAT", "BEST STAT", "DESIRED STAT", "DESIRED STAT", "DESIRED STAT", "DESIRED STAT", "NEGATIVE STAT"])  # Header row
            writer.writerows(self.normalized_data)

        print("Combined and normalized CSV created: combined_normalized_rivens.csv")



