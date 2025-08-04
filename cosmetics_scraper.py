"""
Cosmetics scraper class converted from notebook
"""
import os
import re
import csv
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Tuple, Optional


class CosmeticsScraper:
    """Class to scrape cosmetics/skins data from League Wiki"""
    
    def __init__(self, output_dir="data", max_threads=10):
        """Initialize the cosmetics scraper"""
        self.url_base = "https://wiki.leagueoflegends.com/en-us"
        self.cosmetics_links = {}
        self.paren_pattern = re.compile(r"\s*\([^)]*\)")
        self.max_threads = max_threads
        self.output_dir = output_dir
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def scrape_champion_cosmetics(self, champ_name: str) -> Tuple[str, Optional[Dict], Optional[str]]:
        """
        Scrape cosmetics for a specific champion (same logic as notebook)
        """
        local_links = {}
        try:
            response = requests.get(f"{self.url_base}/{champ_name}/Cosmetics")
            if not response.ok:
                return champ_name, None, f"[!] Failed to load cosmetics page for {champ_name}"

            soup = BeautifulSoup(response.text, "html.parser")
            divs = soup.find_all("div", style="font-size:small")
            if not divs:
                return champ_name, None, f"[=] No cosmetics found for {champ_name}"

            skins_dir = os.path.join("Champions", champ_name, "skins")
            os.makedirs(skins_dir, exist_ok=True)

            skin_blocks = []
            for div in divs:
                skin_blocks.extend(div.select('div[style*="display:inline-block"]'))

            for item in skin_blocks:
                name_div = item.select_one('div[style*="float:left"]')
                skin_name = name_div.find(string=True, recursive=False).strip() if name_div else None
                skin_name = self.paren_pattern.sub("", skin_name).strip()

                file_link_tag = item.select_one('a.mw-file-description[href]')
                href = file_link_tag["href"].split('/')[-1] if file_link_tag else None

                if skin_name and href:
                    local_links[skin_name] = href

            return champ_name, local_links, None

        except Exception as e:
            return champ_name, None, f"[!] Error processing {champ_name}: {e}"
    
    def scrape_all_cosmetics(self, champion_data: list) -> Dict:
        """
        Scrape cosmetics for all champions using multithreading (same as notebook)
        """
        # Multithreaded execution (same as notebook)
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {executor.submit(self.scrape_champion_cosmetics, name): name for name in champion_data}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Scraping Champions", unit="champ"):
                champ_name, data, error = future.result()
                if error:
                    tqdm.write(error)
                elif data:
                    self.cosmetics_links[champ_name] = data
        
        return self.cosmetics_links
    
    def read_cosmetics_from_csv(self, csv_file_path: str) -> Dict:
        """
        Read cosmetics data from a CSV file
        
        Args:
            csv_file_path: Path to the CSV file containing cosmetics data
            
        Returns:
            Dictionary of cosmetics links organized by champion
        """
        cosmetics_data = {}
        
        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    champion = row.get('Champion', '').strip()
                    skin = row.get('Skin', '').strip()
                    image_url = row.get('Image URL', '').strip()
                    
                    if champion and skin and image_url:
                        # Extract filename from URL
                        filename = image_url.split('/')[-1]
                        
                        # Initialize champion dict if not exists
                        if champion not in cosmetics_data:
                            cosmetics_data[champion] = {}
                        
                        # Add skin data
                        cosmetics_data[champion][skin] = filename
            
            print(f"✅ Loaded cosmetics data for {len(cosmetics_data)} champions from {csv_file_path}")
            self.cosmetics_links = cosmetics_data
            return cosmetics_data
            
        except FileNotFoundError:
            print(f"❌ Error: CSV file '{csv_file_path}' not found")
            return {}
        except Exception as e:
            print(f"❌ Error reading cosmetics CSV file: {e}")
            return {}
    
    def save_cosmetics_to_csv(self, filename="cosmetic_links.csv"):
        """
        Save cosmetics data to CSV file (same logic as notebook)
        """
        file_path = os.path.join(self.output_dir, filename)

        with open(file_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Champion", "Skin", "Image URL"])

            for champ, skins in self.cosmetics_links.items():
                for raw_skin, href in skins.items():
                    # Remove champ name from skin if it ends with it (e.g., "Spirit Blossom Ahri" -> "Spirit Blossom")
                    suffix = f" {champ}"
                    if raw_skin.endswith(suffix):
                        skin = raw_skin.removesuffix(suffix)
                    else:
                        skin = raw_skin

                    # Handle relative or absolute URL
                    full_url = f"https://wiki.leagueoflegends.com{href}" if href.startswith("/") else href
                    writer.writerow([champ, skin, full_url])
        
        print(f"Cosmetics data saved to: {file_path}")
    
    def get_cosmetics_links(self) -> Dict:
        """Get the cosmetics links dictionary"""
        return self.cosmetics_links


# Example usage (same as notebook)
if __name__ == "__main__":
    # First get champion data
    from champion_scraper import ChampionScraper
    
    champion_scraper = ChampionScraper()
    
    # Check if champion_names.csv exists and read from it, otherwise scrape
    csv_path = os.path.join("data", "champion_names.csv")
    if os.path.exists(csv_path):
        print(f"📁 Found existing champion CSV file: {csv_path}")
        champion_data = champion_scraper.read_champions_from_csv(csv_path)
    else:
        print("🌐 No champion CSV found, scraping champions from web...")
        champion_data = champion_scraper.get_champion_list()
    
    # Then check if cosmetics CSV exists and read from it, otherwise scrape
    cosmetics_scraper = CosmeticsScraper()
    cosmetics_csv_path = os.path.join("data", "cosmetic_links.csv")
    
    if os.path.exists(cosmetics_csv_path):
        print(f"📁 Found existing cosmetics CSV file: {cosmetics_csv_path}")
        cosmetics_links = cosmetics_scraper.read_cosmetics_from_csv(cosmetics_csv_path)
    else:
        print("🌐 No cosmetics CSV found, scraping cosmetics from web...")
        cosmetics_links = cosmetics_scraper.scrape_all_cosmetics(champion_data)
        cosmetics_scraper.save_cosmetics_to_csv() 