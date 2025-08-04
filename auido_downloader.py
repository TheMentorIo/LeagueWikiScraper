import os
import csv
import hashlib
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

class AudioDownloader:
    def __init__(self, champion_data, base_url="https://wiki.leagueoflegends.com/en-us/{}/Audio", 
                 site_root="https://wiki.leagueoflegends.com", 
                 output_dir="data", 
                 max_threads=10):
        self.champion_data = champion_data
        self.base_url = base_url
        self.site_root = site_root
        self.output_dir = output_dir
        self.max_threads = max_threads
        self.tasks = []
        self.csv_mappings = {}  # champ_name -> list of dicts

    def sanitize(self, text):
        """Sanitize text for filename"""
        return text.replace(" ", "_").replace("/", "-").replace('"', "").replace("'", "").strip()

    def compute_hash(self, data):
        """Compute SHA256 hash of data"""
        return hashlib.sha256(data).hexdigest()

    def compute_file_hash(self, path):
        """Compute hash of file"""
        with open(path, 'rb') as f:
            return self.compute_hash(f.read())

    def download_audio(self, champ_name, category, subcategory, mwtitle, quote_text, audio_url, csv_map):
        """Download audio file and add to CSV mapping"""
        filename = self.sanitize(mwtitle)
        folder = os.path.join(self.output_dir, champ_name, "audio", self.sanitize(category), self.sanitize(subcategory or ""))
        os.makedirs(folder, exist_ok=True)
        save_path = os.path.join(folder, filename)

        try:
            # Download into memory
            r = requests.get(audio_url, stream=True, timeout=15)
            r.raise_for_status()
            content = b''.join(r.iter_content(8192))
            remote_hash = self.compute_hash(content)

            # Compare hash if file exists
            if os.path.exists(save_path):
                local_hash = self.compute_file_hash(save_path)
                if local_hash == remote_hash:
                    print(f"✅ Skipped (unchanged): {filename}")
                else:
                    with open(save_path, 'wb') as f:
                        f.write(content)
                    print(f"⬇️ Updated: {filename}")
            else:
                with open(save_path, 'wb') as f:
                    f.write(content)
                print(f"⬇️ Downloaded: {filename}")

            # Add to CSV mapping
            csv_map.append({
                "Download Filename": filename,
                "Quote Text": quote_text,
                "Category": category,
                "Subcategory": subcategory or "",
                "URL": audio_url
            })

        except Exception as e:
            print(f"❌ Failed: {filename} - {e}")

    def collect_tasks(self):
        """Collect all download tasks from champion pages"""
        for champ in tqdm(self.champion_data, desc="Parsing champions"):
            self.csv_mappings[champ] = []

            try:
                res = requests.get(self.base_url.format(champ))
                res.raise_for_status()
                soup = BeautifulSoup(res.text, "html.parser")

                content_div = soup.find("div", id="mw-content-text")
                current_category = "Uncategorized"
                current_subcategory = None

                for element in content_div.find_all(["h2", "h3", "ul"], recursive=True):
                    if element.name == "h2":
                        headline = element.find("span", class_="mw-headline")
                        current_category = headline.get_text(strip=True) if headline else element.get_text(strip=True)
                        current_subcategory = None

                    elif element.name == "h3":
                        headline = element.find("span", class_="mw-headline")
                        if headline and headline.get("id", "").startswith("Using_"):
                            span = headline.find("span", {"style": "white-space:normal;"})
                            link = span.find("a") if span else None
                            if link:
                                current_subcategory = link.get_text(strip=True)
                            else:
                                current_subcategory = headline.get_text(strip=True).replace("Using", "").strip()
                        else:
                            current_subcategory = None

                    elif element.name == "ul":
                        for li in element.find_all("li"):
                            quote_tag = li.find("i")
                            if not quote_tag:
                                continue
                            quote = quote_tag.get_text(strip=True)

                            for audio_tag in li.find_all("audio"):
                                mwtitle = audio_tag.get("data-mwtitle", "")
                                if "Original" not in mwtitle:
                                    continue

                                source = audio_tag.find("source")
                                if not source:
                                    continue
                                src = source.get("src", "")
                                if not src:
                                    continue

                                audio_url = urljoin(self.site_root, src.split("?")[0])
                                self.tasks.append((
                                    champ, current_category, current_subcategory,
                                    mwtitle, quote, audio_url, self.csv_mappings[champ]
                                ))

            except Exception as e:
                print(f"❌ Error parsing {champ}: {e}")

    def download_all(self):
        """Download all audio files using multithreading"""
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = [
                executor.submit(self.download_audio, champ, cat, subcat, mwtitle, quote, url, mapping)
                for champ, cat, subcat, mwtitle, quote, url, mapping in self.tasks
            ]
            for _ in tqdm(as_completed(futures), total=len(futures), desc="Downloading audio", unit="file"):
                pass

    def write_csvs(self):
        """Write CSV mapping files for each champion"""
        for champ, mapping in self.csv_mappings.items():
            if not mapping:
                continue
            csv_folder = os.path.join(self.output_dir, champ)
            os.makedirs(csv_folder, exist_ok=True)
            csv_path = os.path.join(csv_folder, "audio_mapping.csv")

            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["Download Filename", "Quote Text", "Category", "Subcategory", "URL"])
                writer.writeheader()
                writer.writerows(mapping)

    def run(self):
        """Run the complete audio download process"""
        self.collect_tasks()
        self.download_all()
        self.write_csvs()
        print("🎉 All audio downloads and mappings complete.")

# Usage example:
if __name__ == "__main__":
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
    champion_data=["Nunu"]
    downloader = AudioDownloader(champion_data)
    downloader.run()