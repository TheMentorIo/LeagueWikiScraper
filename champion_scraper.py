"""
Champion scraper class converted from notebook
"""
import os
import csv
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from typing import List


class ChampionScraper:
    """Class to scrape champion data from League Wiki"""
    
    def __init__(self, output_dir="data"):
        """Initialize the scraper"""
        self.champion_data = []
        self.url = "https://wiki.leagueoflegends.com/"
        self.output_dir = output_dir
        
        # Create output directory (same as notebook)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_champion_list(self) -> List[str]:
        """
        Get list of all champions from the wiki
        Returns the same champion data as the original notebook code
        """
        response = requests.get(f"{self.url}/en-us")
        if response.ok:
            soup = BeautifulSoup(response.text, "html.parser")
            grid = soup.find("div", id="champion-grid")

            if grid:
                links = grid.find_all("a", href=True)

                for a_tag in tqdm(links, desc="Parsing champion links"):
                    href = a_tag["href"]

                    # Decode and format the champion name
                    name = href.rstrip("/").split("/")[-1]
                    # Add to dictionary
                    self.champion_data.append(name)

            else:
                print("Champion grid not found.")
        else:
            print(f"Failed to load page: {response.status_code}")
        
        return self.champion_data
    
    def read_champions_from_csv(self, csv_file_path: str) -> List[str]:
        """
        Read champion names from a CSV file
        
        Args:
            csv_file_path: Path to the CSV file containing champion names
            
        Returns:
            List of champion names from the CSV file
        """
        champion_names = []
        
        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                
                # Skip header if it exists
                header = next(reader, None)
                if header and header[0].lower() == 'champion':
                    # Header exists, continue reading data
                    pass
                else:
                    # No header, reset file pointer to beginning
                    f.seek(0)
                    reader = csv.reader(f)
                
                for row in reader:
                    if row and row[0].strip():  # Check if row is not empty
                        champion_names.append(row[0].strip())
            
            print(f"✅ Loaded {len(champion_names)} champions from {csv_file_path}")
            self.champion_data = champion_names
            return champion_names
            
        except FileNotFoundError:
            print(f"❌ Error: CSV file '{csv_file_path}' not found")
            return []
        except Exception as e:
            print(f"❌ Error reading CSV file: {e}")
            return []
    
    def save_champions_to_csv(self, filename="champion_names.csv"):
        """
        Save champion data to CSV file (same logic as notebook)
        """
        file_path = os.path.join(self.output_dir, filename)

        with open(file_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Champion"])  # header

            for name in self.champion_data:
                writer.writerow([name])
        
        print(f"Champion data saved to: {file_path}")
    
    def print_champions(self):
        """Print all champion names (same as original notebook)"""
        for name in self.champion_data:
            print(name)
    
    def get_champion_data(self) -> List[str]:
        """Get the champion data list"""
        return self.champion_data


# Example usage (same as notebook)
if __name__ == "__main__":
    choice = 0  # Initialize variable

    # Loop until valid choice
    while choice not in [1, 2]:
        try:
            choice = int(input("Option 1 for scrape || Option 2 to read from csv: "))
        except ValueError:
            print("Please enter a valid number (1 or 2).")

    scraper = ChampionScraper()

    if choice == 1:
        scraper.get_champion_list()
        scraper.print_champions()
        scraper.save_champions_to_csv()
    elif choice == 2:
        scraper.read_champions_from_csv("champion_names.csv")
        scraper.print_champions()
