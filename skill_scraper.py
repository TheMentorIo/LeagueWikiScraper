import os
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

class SkillScraper:
    def __init__(self, champion_data, csv_path="data/champion_names.csv"):
        self.champion_scraper = champion_scraper
        self.csv_path = csv_path
        self.base_url = "https://wiki.leagueoflegends.com/en-us/"
        self.output_dir = "data"
        self.skills = ["skill_innate", "skill_q", "skill_w", "skill_e", "skill_r"]
        self.MAX_THREADS = 10
        self.champion_data = champion_data

    def load_champion_data(self):
        if os.path.exists(self.csv_path):
            print(f"📁 Found existing champion CSV file: {self.csv_path}")
            return self.champion_scraper.read_champions_from_csv(self.csv_path)
        else:
            print("🌐 No champion CSV found, scraping champions from web...")
            return self.champion_scraper.get_champion_list()

    def sanitize(self, text):
        return text.replace(" ", "_").replace("/", "-").replace('"', "").replace("'", "").strip()

    def compute_hash(self, data):
        return hashlib.sha256(data).hexdigest()

    def compute_file_hash(self, path):
        with open(path, 'rb') as f:
            return self.compute_hash(f.read())

    def download_image_if_not_exists(self, url, save_path, session):
        try:
            r = session.get(url, stream=True, timeout=10)
            r.raise_for_status()
            content = b''.join(r.iter_content(8192))
            remote_hash = self.compute_hash(content)

            if os.path.exists(save_path):
                local_hash = self.compute_file_hash(save_path)
                if local_hash == remote_hash:
                    tqdm.write(f"✅ Skipped (unchanged): {os.path.basename(save_path)}")
                    return "Skipped"

            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(content)
            tqdm.write(f"⬇️  Downloaded: {os.path.basename(save_path)}")
            return "Downloaded"

        except Exception as e:
            tqdm.write(f"❌ Failed to download {url} - {e}")
            return "Error"

    def process_champion(self, champ):
        session = requests.Session()
        try:
            res = session.get(f"{self.base_url}{champ}")
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")

            card = soup.find("div", class_="infobox champion-upd")
            if not card:
                tqdm.write(f"❌ No infobox found for {champ}")
                return

            table = card.find("table")
            spans = table.find_all("span")
            champ_name = spans[0].get_text(strip=True)
            champ_title = spans[1].get_text(strip=True)

            info_data = {
                "Champion": champ_name,
                "Title": champ_title
            }

            rows = card.find_all("div", class_="infobox-data-row championbox")
            for row in rows:
                label_tag = row.find("div", class_="infobox-data-label")
                value_tag = row.find("div", class_="infobox-data-value")
                if not label_tag or not value_tag:
                    continue
                label = label_tag.get_text(strip=True)
                if label == "Last changed":
                    continue
                value = " ".join(value_tag.stripped_strings)
                info_data[label] = value

            champ_dir = os.path.join(self.output_dir, champ_name)
            os.makedirs(champ_dir, exist_ok=True)

            # === Save info.csv ===
            info_csv_path = os.path.join(champ_dir, "info.csv")
            with open(info_csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=info_data.keys())
                writer.writeheader()
                writer.writerow(info_data)

            # === Process skills ===
            skill_csv_data = []
            skill_folder_map = {
                "skill_innate": "passive",
                "skill_q": "q",
                "skill_w": "w",
                "skill_e": "e",
                "skill_r": "r"
            }
            for skill in self.skills:
                try:
                    div = soup.find("div", class_=skill)
                    if not div:
                        continue

                    skill_name_tag = div.find("div", class_="ability-info-stats__ability")
                    if not skill_name_tag:
                        continue

                    skill_name = skill_name_tag.get_text(strip=True)
                    icon_divs = div.find_all("div", class_="ability-info-icon")

                    for idx, icon_div in enumerate(icon_divs):
                        try:
                            img_tag = icon_div.find("img", src=True)
                            if not img_tag:
                                continue

                            src = img_tag['src'].split("?")[0]
                            full_url = urljoin(self.base_url, src)
                            ext = os.path.splitext(src)[1] or ".png"
                            safe_skill_name = self.sanitize(skill_name)
                            folder = skill_folder_map.get(skill, "other")
                            # Save in .../skills/q or w or e or r or passive
                            save_path = os.path.join(champ_dir, "skills", folder, f"{safe_skill_name}_{idx+1}{ext}")

                            status = self.download_image_if_not_exists(full_url, save_path, session)

                            skill_csv_data.append({
                                "Skill": skill_name,
                                "ImageFile": os.path.join("skills", folder, f"{safe_skill_name}_{idx+1}{ext}")
                            })

                        except Exception as e:
                            tqdm.write(f"⚠️ Error processing image #{idx+1} for {skill_name} - {e}")

                except Exception as e:
                    tqdm.write(f"⚠️ Error processing skill '{skill}' for {champ_name} - {e}")

            # === Save skills.csv ===
            if skill_csv_data:
                try:
                    skill_csv_path = os.path.join(champ_dir, "skills.csv")
                    with open(skill_csv_path, "w", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=skill_csv_data[0].keys())
                        writer.writeheader()
                        writer.writerows(skill_csv_data)
                except Exception as e:
                    tqdm.write(f"❌ Failed to write skills.csv for {champ_name} - {e}")

        except Exception as e:
            tqdm.write(f"❌ Error processing {champ}: {e}")

    def run(self):
        with ThreadPoolExecutor(max_workers=self.MAX_THREADS) as executor:
            futures = [executor.submit(self.process_champion, champ) for champ in self.champion_data]
            for future in tqdm(as_completed(futures), total=len(futures), desc="Processing Champions"):
                future.result()  # Ensures exceptions inside threads are raised here
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
    skill_scraper = SkillScraper(champion_data)
    skill_scraper.run()