""" Kodi addons.xml generator for release repository """

import os
import hashlib
import zipfile
from xml.dom import minidom
import re

class Generator:
    def __init__(self):
        if not os.path.exists("zips"):
            os.makedirs("zips")
        
        self._generate_addons_file()
        self._generate_md5_file()
        print("✅ Finished updating addons.xml and addons.xml.md5")

    def _get_latest_zip_version(self, addon_folder):
        """Find the latest version zip file in an addon folder"""
        if not os.path.exists(addon_folder):
            return None
        
        zip_files = [f for f in os.listdir(addon_folder) if f.endswith('.zip')]
        if not zip_files:
            return None
        
        # Sort by version number (extract version from filename)
        def extract_version(filename):
            match = re.search(r'-(\d+\.\d+\.\d+)\.zip', filename)
            if match:
                version = match.group(1)
                return tuple(map(int, version.split('.')))
            return (0, 0, 0)
        
        zip_files.sort(key=extract_version, reverse=True)
        return os.path.join(addon_folder, zip_files[0])

    def _extract_addon_xml_from_zip(self, zip_path):
        """Extract addon.xml content from a zip file"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Find addon.xml in the zip (could be in root or subfolder)
                for file_name in zip_ref.namelist():
                    if file_name.endswith('addon.xml'):
                        with zip_ref.open(file_name) as xml_file:
                            return xml_file.read().decode('utf-8')
        except Exception as e:
            print(f"❌ Error reading {zip_path}: {e}")
        return None

    def _clean_xml_content(self, xml_content):
        """Remove XML declaration and clean up content"""
        lines = xml_content.splitlines()
        cleaned = []
        for line in lines:
            if '<?xml' not in line:
                cleaned.append(line.rstrip())
        return '\n'.join(cleaned)

    def _generate_addons_file(self):
        addons_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<addons>\n'
        
        # 1. Add repository addon from root
        print("📦 Processing repository addon...")
        if os.path.exists("addon.xml"):
            try:
                with open("addon.xml", "r", encoding="utf-8") as f:
                    repo_xml = self._clean_xml_content(f.read())
                    addons_xml += repo_xml + "\n\n"
                    print("✅ Added repository addon")
            except Exception as e:
                print(f"❌ Error reading repository addon.xml: {e}")
        
        # 2. Add plugin addons from zips folder
        zips_dir = "zips"
        if os.path.exists(zips_dir):
            for addon_folder in os.listdir(zips_dir):
                addon_path = os.path.join(zips_dir, addon_folder)
                
                # Skip files and system folders
                if not os.path.isdir(addon_path) or addon_folder.startswith('.'):
                    continue
                
                print(f"📦 Processing {addon_folder}...")
                
                # Find latest zip
                latest_zip = self._get_latest_zip_version(addon_path)
                if not latest_zip:
                    print(f"⚠️  No zip files found in {addon_folder}")
                    continue
                
                print(f"   Using: {os.path.basename(latest_zip)}")
                
                # Extract addon.xml from zip
                xml_content = self._extract_addon_xml_from_zip(latest_zip)
                if xml_content:
                    cleaned_xml = self._clean_xml_content(xml_content)
                    addons_xml += cleaned_xml + "\n\n"
                    print(f"✅ Added {addon_folder}")
                else:
                    print(f"❌ Could not extract addon.xml from {addon_folder}")
        
        addons_xml = addons_xml.strip() + "\n</addons>\n"
        
        # Write addons.xml
        output_path = os.path.join("zips", "addons.xml")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(addons_xml)
        
        print(f"\n📄 Generated: {output_path}")

    def _generate_md5_file(self):
        """Generate MD5 checksum for addons.xml"""
        try:
            addons_xml_path = os.path.join("zips", "addons.xml")
            with open(addons_xml_path, "r", encoding="utf-8") as f:
                m = hashlib.md5(f.read().encode("utf-8")).hexdigest()
            
            md5_path = os.path.join("zips", "addons.xml.md5")
            with open(md5_path, "w") as f:
                f.write(m)
            
            print(f"🔐 Generated: {md5_path}")
            print(f"   MD5: {m}")
        except Exception as e:
            print(f"❌ Error creating addons.xml.md5: {e}")

if __name__ == "__main__":
    print("🚀 Kodi Repository Generator\n")
    Generator()
