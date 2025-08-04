"""
Champion image scraper class converted from notebook
"""
import csv
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from typing import Dict, Tuple


class ChampionImageScraper:
    """Class to scrape champion images from League Wiki"""
    
    def __init__(self, output_dir="data", max_threads=8):
        """Initialize the image scraper"""
        self.base_url = "https://wiki.leagueoflegends.com/en-us"
        self.categories = ["Splashes", "Loading", "Circles", "Squares", "Centered", "Tiles"]
        self.max_threads = max_threads
        self.output_dir = output_dir
        self.champion_results = {}
    
    def scrape_champion(self, champ_name: str, skins: Dict) -> Tuple[str, Dict]:
        """
        Scrape champion images (same logic as notebook)
        """
        champion_data = {}
        for skin_name, skin_path in skins.items():
            try:
                response = requests.get(f"{self.base_url}/{skin_path}", timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")
            except Exception as e:
                print(f"[ERROR] {champ_name} - {skin_name}: {e}")
                continue

            skin_data = {}

            for category in self.categories:
                div = soup.find("div", {"data-title": category})
                if not div:
                    continue

                images = {}
                for a in div.find_all("a"):
                    title = a.get("title")
                    href = a.get("href")
                    if title and href:
                        images[title] = href.split("/")[-1].split(":")[-1]

                if images:
                    skin_data[category] = images

            if skin_data:
                champion_data[skin_name] = skin_data

        return champ_name, champion_data
    
    def scrape_all_champions(self, cosmetics_links: Dict) -> Dict:
        """
        Scrape all champion images using multithreading (same as notebook)
        """
        # Run with multithreading (same as notebook)
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = [
                executor.submit(self.scrape_champion, champ_name, cosmetics_links[champ_name])
                for champ_name in cosmetics_links
            ]

            for future in tqdm(as_completed(futures), total=len(futures), desc="Scraping Champions"):
                champ_name, data = future.result()
                self.champion_results[champ_name] = data
        
        return self.champion_results
    
    def read_images_from_csv(self, csv_file_path: str) -> Dict:
        """
        Read champion image data from a CSV file
        
        Args:
            csv_file_path: Path to the CSV file containing champion image data
            
        Returns:
            Dictionary of champion image data organized by champion and skin
        """
        champion_data = {}
        
        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    champion = row.get('Champion', '').strip()
                    skin = row.get('Skin', '').strip()
                    category = row.get('Category', '').strip()
                    image_title = row.get('Image Title', '').strip()
                    url_fragment = row.get('Image URL Fragment', '').strip()
                    
                    if champion and skin and category and image_title and url_fragment:
                        # Initialize champion dict if not exists
                        if champion not in champion_data:
                            champion_data[champion] = {}
                        
                        # Initialize skin dict if not exists
                        if skin not in champion_data[champion]:
                            champion_data[champion][skin] = {}
                        
                        # Initialize category dict if not exists
                        if category not in champion_data[champion][skin]:
                            champion_data[champion][skin][category] = {}
                        
                        # Add image data
                        champion_data[champion][skin][category][image_title] = url_fragment
            
            print(f"✅ Loaded champion image data for {len(champion_data)} champions from {csv_file_path}")
            self.champion_results = champion_data
            return champion_data
            
        except FileNotFoundError:
            print(f"❌ Error: CSV file '{csv_file_path}' not found")
            return {}
        except Exception as e:
            print(f"❌ Error reading champion image CSV file: {e}")
            return {}
    
    def save_images_to_csv(self, filename="champion_images.csv"):
        """
        Save champion image data to CSV file (same logic as notebook)
        """
        output_path = f"{self.output_dir}/{filename}"

        with open(output_path, "w", newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Champion", "Skin", "Category", "Image Title", "Image URL Fragment"])

            for champ_name, skins in self.champion_results.items():
                for raw_skin_name, categories in skins.items():
                    suffix = f" {champ_name}"
                    if raw_skin_name.endswith(suffix):
                        skin_name = raw_skin_name.removesuffix(suffix)
                    else:
                        skin_name = raw_skin_name

                    for category, images in categories.items():
                        for title, url_fragment in images.items():
                            writer.writerow([champ_name, skin_name, category, title, url_fragment])
        
        print(f"Champion image data saved to: {output_path}")
    
    def get_champion_results(self) -> Dict:
        """Get the champion results dictionary"""
        return self.champion_results


# Example usage (same as notebook)
if __name__ == "__main__":
    # First get cosmetics data
    from cosmetics_scraper import CosmeticsScraper
    from champion_scraper import ChampionScraper
    
    import os
    
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
    
    # Then check if champion images CSV exists and read from it, otherwise scrape
    image_scraper = ChampionImageScraper()
    images_csv_path = os.path.join("data", "champion_images.csv")
    
    if os.path.exists(images_csv_path):
        print(f"📁 Found existing champion images CSV file: {images_csv_path}")
        champion_results = image_scraper.read_images_from_csv(images_csv_path)
    else:
        print("🌐 No champion images CSV found, scraping images from web...")
        champion_results = image_scraper.scrape_all_champions(cosmetics_links)
        image_scraper.save_images_to_csv() 