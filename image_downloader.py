"""
Image downloader class converted from notebook
"""
import os
import hashlib
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict
from datetime import datetime


class ImageDownloader:
    """Class to download champion images from League Wiki"""
    
    def __init__(self, output_dir="data", max_threads=10):
        """Initialize the image downloader"""
        self.base_url = "https://wiki.leagueoflegends.com/en-us/images/"
        self.output_dir = output_dir
        self.max_threads = max_threads
        self.log_file = os.path.join(output_dir, "download_errors.log")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def log_error(self, message: str):
        """
        Log error messages to file with timestamp
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"❌ Failed to write to log file: {e}")
    
    def compute_hash(self, data):
        """Helper: compute SHA256 hash of a file or bytes (same as notebook)"""
        hasher = hashlib.sha256()
        hasher.update(data)
        return hasher.hexdigest()
    
    def compute_file_hash(self, path):
        """Compute file hash (same as notebook)"""
        with open(path, 'rb') as f:
            return self.compute_hash(f.read())
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for Windows file system
        Remove or replace invalid characters
        """
        # Characters not allowed in Windows filenames
        invalid_chars = '<>:"|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        # Ensure filename is not empty
        if not filename:
            filename = "unnamed"
        
        return filename
    
    def download_image_if_changed(self, image_url: str, save_path: str):
        """
        Download with local hash check (same logic as notebook)
        """
        try:
            # Check if file exists
            if os.path.exists(save_path):
                local_hash = self.compute_file_hash(save_path)
            else:
                local_hash = None

            # Download image into memory
            response = requests.get(image_url, stream=True, timeout=15)
            response.raise_for_status()
            content = b''.join(response.iter_content(chunk_size=8192))
            remote_hash = self.compute_hash(content)

            if local_hash and local_hash == remote_hash:
                print(f"✅ Skipped (unchanged): {image_url}")
                return

            # Save new or changed file
            with open(save_path, 'wb') as f:
                f.write(content)
            print(f"⬇️ Downloaded: {image_url}")

        except Exception as e:
            error_msg = f"❌ Error downloading {image_url}: {e}"
            print(error_msg)
            self.log_error(error_msg)
    
    def download_all_images(self, champion_results: Dict):
        """
        Download all images using multithreading (same as notebook)
        """
        futures = []
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            for champ_name, skins in tqdm(champion_results.items(), desc="Champions", unit="champ"):
                for skin_name, categories in skins.items():
                    for category, image_data in categories.items():
                        if not isinstance(image_data, dict):
                            continue

                        # Sanitize folder names
                        safe_champ_name = self.sanitize_filename(champ_name)
                        safe_skin_name = self.sanitize_filename(skin_name)
                        
                        # Create path structure: data/champname/skins/category
                        folder_path = os.path.join(self.output_dir, safe_champ_name, "skins", safe_skin_name, category)
                        os.makedirs(folder_path, exist_ok=True)

                        for version_label, filename in image_data.items():
                            image_url = self.base_url + filename
                            ext = os.path.splitext(filename)[1]
                            safe_name = self.sanitize_filename(version_label.replace(" ", "_").replace("/", "-")) + ext
                            save_path = os.path.join(folder_path, safe_name)

                            futures.append(executor.submit(self.download_image_if_changed, image_url, save_path))

            for _ in tqdm(as_completed(futures), total=len(futures), desc="Processing images", unit="img"):
                pass

        print("🎉 Done. Only changed or new images were downloaded.")
        print(f"📝 Error log saved to: {self.log_file}")


# Example usage (same as notebook)
if __name__ == "__main__":
    # First get champion results from image scraper
    from champion_image_scraper import ChampionImageScraper
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
    
    # Download all images
    downloader = ImageDownloader()
    downloader.download_all_images(champion_results) 