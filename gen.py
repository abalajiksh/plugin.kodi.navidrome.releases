""" Kodi addons.xml generator for release repository """

import os
import hashlib
import zipfile
import re
import shutil

class Generator:
    def __init__(self):
        if not os.path.exists("zips"):
            os.makedirs("zips")
        
        self._generate_addons_file()
        self._generate_md5_file()
        self._create_repository_zip()
        print("\n✅ Finished updating repository files")

    def _get_latest_zip_version(self, addon_folder):
        """Find the latest version zip file in an addon folder"""
        if not os.path.exists(addon_folder):
            return None
        
        zip_files = [f for f in os.listdir(addon_folder) if f.endswith('.zip')]
        if not zip_files:
            return None
        
        # Sort by version number
        def extract_version(filename):
            # Handle malformed filenames like plugin.kodi.navidrome-.0.3.2.zip
            match = re.search(r'-?(\d+)\.(\d+)\.(\d+)\.zip', filename)
            if match:
                return tuple(map(int, match.groups()))
            return (0, 0, 0)
        
        zip_files.sort(key=extract_version, reverse=True)
        return os.path.join(addon_folder, zip_files[0])

    def _extract_addon_xml_from_zip(self, zip_path):
        """Extract addon.xml content from a zip file"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_name in zip_ref.namelist():
                    if file_name.endswith('addon.xml') and '/' not in file_name[:-9]:
                        # Get addon.xml from root of zip only
                        with zip_ref.open(file_name) as xml_file:
                            return xml_file.read().decode('utf-8')
        except Exception as e:
            print(f"  ❌ Error reading {os.path.basename(zip_path)}: {e}")
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
        print("🚀 Generating addons.xml...\n")
        addons_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<addons>\n'
        
        # 1. Add repository addon from root
        print("📦 Processing repository addon...")
        if os.path.exists("addon.xml"):
            try:
                with open("addon.xml", "r", encoding="utf-8") as f:
                    repo_xml = self._clean_xml_content(f.read())
                    addons_xml += repo_xml + "\n\n"
                    print("  ✅ Added repository.kodi.navidrome")
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        # 2. Add plugin addons from zips folder
        zips_dir = "zips"
        if os.path.exists(zips_dir):
            for addon_folder in os.listdir(zips_dir):
                addon_path = os.path.join(zips_dir, addon_folder)
                
                if not os.path.isdir(addon_path) or addon_folder.startswith('.'):
                    continue
                
                print(f"\n📦 Processing {addon_folder}...")
                
                latest_zip = self._get_latest_zip_version(addon_path)
                if not latest_zip:
                    print(f"  ⚠️  No zip files found")
                    continue
                
                print(f"  📎 Using: {os.path.basename(latest_zip)}")
                
                xml_content = self._extract_addon_xml_from_zip(latest_zip)
                if xml_content:
                    cleaned_xml = self._clean_xml_content(xml_content)
                    addons_xml += cleaned_xml + "\n"
                    
                    # Extract addon ID and version
                    addon_id_match = re.search(r'id="([^"]+)"', xml_content)
                    version_match = re.search(r'version="([^"]+)"', xml_content)
                    if addon_id_match and version_match:
                        print(f"  ✅ Added {addon_id_match.group(1)} v{version_match.group(1)}")
                else:
                    print(f"  ❌ Could not extract addon.xml")
        
        addons_xml = addons_xml.strip() + "\n</addons>\n"
        
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
            
            print(f"🔐 Generated: {md5_path} (MD5: {m})")
        except Exception as e:
            print(f"❌ Error creating MD5: {e}")

    def _create_repository_zip(self):
        """Create a zip file of the repository addon for easy installation"""
        try:
            # Read version from addon.xml
            with open("addon.xml", "r", encoding="utf-8") as f:
                content = f.read()
                version_match = re.search(r'version="([^"]+)"', content)
                version = version_match.group(1) if version_match else "1.0.0"
            
            zip_filename = f"repository.kodi.navidrome-{version}.zip"
            zip_path = os.path.join("zips", zip_filename)
            
            # Create zip with required files
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write("addon.xml", "repository.kodi.navidrome/addon.xml")
                if os.path.exists("icon.png"):
                    zipf.write("icon.png", "repository.kodi.navidrome/icon.png")
            
            print(f"📦 Created: {zip_path}")
            print(f"\n💡 Install URL: https://plugin-kodi-navidrome-releases.pages.dev/zips/{zip_filename}")
        except Exception as e:
            print(f"❌ Error creating repository zip: {e}")

if __name__ == "__main__":
    print("="*60)
    print("  Kodi Repository Generator")
    print("="*60 + "\n")
    Generator()
