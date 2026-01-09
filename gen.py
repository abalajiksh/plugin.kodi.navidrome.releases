""" Kodi addons.xml generator """

import re
import os
import hashlib
import zipfile
from xml.dom import minidom

class Generator:
    def __init__(self):
        if not os.path.exists("zips"):
            os.makedirs("zips")
        
        self._generate_addons_file()
        self._generate_md5_file()
        print("Finished updating addons.xml and addons.xml.md5")

    def _generate_addons_file(self):
        addons = os.listdir(".")
        addons_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<addons>\n'
        
        for addon in addons:
            try:
                if not os.path.isdir(addon) or addon in ["zips", "docs", ".git"] or addon.startswith("."):
                    continue
                
                xml_path = os.path.join(addon, "addon.xml")
                if not os.path.exists(xml_path):
                    continue
                    
                with open(xml_path, "r", encoding="utf-8") as f:
                    xml_lines = f.read().splitlines()
                
                addon_xml = ""
                for line in xml_lines:
                    if line.find("<?xml") >= 0:
                        continue
                    addon_xml += line.rstrip() + "\n"
                
                addons_xml += addon_xml.rstrip() + "\n\n"
                
            except Exception as e:
                print(f"Excluding {addon} for {e}")
        
        addons_xml = addons_xml.strip() + "\n</addons>\n"
        
        with open(os.path.join("zips", "addons.xml"), "w", encoding="utf-8") as f:
            f.write(addons_xml)

    def _generate_md5_file(self):
        try:
            with open(os.path.join("zips", "addons.xml"), "r", encoding="utf-8") as f:
                m = hashlib.md5(f.read().encode("utf-8")).hexdigest()
            
            with open(os.path.join("zips", "addons.xml.md5"), "w") as f:
                f.write(m)
        except Exception as e:
            print(f"Error creating addons.xml.md5: {e}")

if __name__ == "__main__":
    Generator()

