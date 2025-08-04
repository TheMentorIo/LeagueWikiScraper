from calendar import c
from nt import replace
import os
from unicodedata import category
from urllib.parse import unquote
import shutil
import csv

class SkinDataProcessor:
    def __init__(self):
        self.path = "data"
        self.champion_image = self.path + "/champion_images.csv"
        self.directories = [d for d in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, d))]
        self.champion_skin_data = {}
        self.load_champions_skin()
        self.cat_art_list=["Centered", "Circles", "Loading", "Splashes", "Squares", "Tiles"]
        self.skills = ["passive","q","r","w","e"]

    def solve_quote_problem(self):
        """Solve quote problem in directory names"""
        for directory in self.directories:
            if "%" in directory:
                os.rename(os.path.join(self.path, directory), os.path.join(self.path, unquote(directory)))

    def repair_naming_problem(self):
        """Repair naming problem that created folder in folder"""
        for directory in self.directories:
            skins = [d for d in os.listdir(os.path.join(self.path, directory)) if os.path.isdir(os.path.join(self.path, directory, d))]
            for skin in skins:
                category = [c for c in os.listdir(os.path.join(self.path, directory, skin)) if os.path.isdir(os.path.join(self.path, directory, skin, c))]
                if len(category) == 1:
                    source = os.path.join(self.path, directory, skin, category[0])
                    to = os.path.join(self.path, directory, skin)
                    for f in os.listdir(source):
                        shutil.move(os.path.join(source, f), to)
                    if not os.listdir(source):  # folder is empty
                        os.rmdir(source)
                        print(f"Removed empty folder: {source}")

    def move_to_skins_folder(self):
        """Move to skins folder"""
        for directory in self.directories:
            skins = [d for d in os.listdir(os.path.join(self.path, directory)) if os.path.isdir(os.path.join(self.path, directory, d))]
            source = os.path.join(self.path, directory)
            to = os.path.join(self.path, directory, "skins")
            os.mkdir(to)
            for skin in skins:
                shutil.move(os.path.join(source, skin), to)

    def repair_mistake(self):
        """Repair mistake the one skin for some champions didn't moved as expected"""
        
        for directory in self.directories:
            skins_folder = os.path.join(self.path, directory, "skins")
            skins = [d for d in os.listdir(skins_folder) if os.path.isdir(os.path.join(skins_folder, d))]
            if self.cat_art_list[0] in skins:
                os.mkdir(os.path.join(self.path, directory, "skins", "change"))
                for file in self.cat_art_list:
                    if file in skins:
                        shutil.move(os.path.join(self.path, directory, "skins", file), os.path.join(self.path, directory, "skins", "change", file))

    def load_champions_skin(self):
        """Load champions skin data"""
        with open(self.champion_image, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                champion = unquote(row['Champion'])
                skin = row['Skin'].replace(":", "_").replace("/", "").rstrip(".")

                # Append skin to a list under the champion key
                if champion not in self.champion_skin_data:
                    self.champion_skin_data[champion] = set()
                
                self.champion_skin_data[champion].add(skin)

    def write_champion_skins_csv(self):
        """Write champion skins to CSV file"""
        with open('data/champion_skins.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Champion', 'Skin'])  # Header

            for champion, skins in self.champion_skin_data.items():
                for skin in skins:
                    writer.writerow([champion, skin])

    def change_required_file_with_true_name(self):
        """Change required file with true name"""
        for champion in self.champion_skin_data:
            source = os.path.join(self.path, champion, "skins")
            dir = [d for d in os.listdir(source) if os.path.isdir(os.path.join(source, d))]
            if "change" in dir:
                print(champion)
                missing = list(set(dir) ^ set(self.champion_skin_data[champion]))
                name = missing[0] if missing[0] != "change" else missing[1]
                os.rename(os.path.join(source, "change"), os.path.join(source, name))

    def show_missing_items(self):
        """Show if something is missing"""
        for champion in self.champion_skin_data:
            source = os.path.join(self.path, champion, "skins")
            dir = [d for d in os.listdir(source) if os.path.isdir(os.path.join(source, d))]
            missing = list(set(dir) ^ set(self.champion_skin_data[champion]))
            if missing:
                print(missing, champion)

    def run_all_operations(self):
        """Run all operations in sequence"""
        # Uncomment the methods you want to run
        # self.solve_quote_problem()
        # self.repair_naming_problem()
        # self.move_to_skins_folder()
        # self.repair_mistake()
        # self.load_champions_skin()
        # self.write_champion_skins_csv()
        # self.change_required_file_with_true_name()
        # self.show_missing_items()
        pass

    def check_art_cat(self):
        """
        For each skin, check which art categories are missing.
        Prints the skin, champion, and missing categories.
        """
        for champion in self.directories:
            skins_folder = os.path.join(self.path, champion, "skins")
            if not os.path.exists(skins_folder):
                continue
            skins = [
                skin for skin in os.listdir(skins_folder)
                if os.path.isdir(os.path.join(skins_folder, skin))
            ]
            for skin in skins:
                skin_folder = os.path.join(skins_folder, skin)
                arts = [
                    art for art in os.listdir(skin_folder)
                    if os.path.isdir(os.path.join(skin_folder, art))
                ]
                missing = set(self.cat_art_list) - set(arts)
                if missing:
                    print(f"Skin '{skin}' of champion '{champion}' is missing: {missing}")
                    
    def check_skill(self):
        for champion in self.directories:
            source = os.path.join(self.path,champion,"skills")
            skills = [skill for skill in os.listdir(source) if os.path.isdir(os.path.join(source,skill))]
            missing = set(skills)^set(self.skills)
            if(missing):
                print(champion)

# Example usage:
if __name__ == "__main__":
    reader =SkinDataProcessor()
    reader.check_skill()