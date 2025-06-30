import os
import ujson as json
import tempfile
import shutil
from zipfile import ZipFile, ZipInfo

from endstone.plugin import Plugin
from endstone_addons.tools.type_getter import get_pack_type
from endstone_addons.types.pack_type import PackType
from endstone_addons.types.path_provider import PathProvider


class AddonsProcessor:
    def process_addons(self, addons_paths: list, plugin: Plugin):
        """
        Processes a list of addon paths. Handles .mcpack, .mcaddon, and multi-pack .zip files.
        """
        for path in addons_paths:
            self._process_addon_file(path, plugin)

    def _process_addon_file(self, path: str, plugin: Plugin):
        """
        Determines the type of addon file and processes it accordingly.
        """
        filename = os.path.basename(path)
        plugin.logger.info(f"Processing {filename}...")

        with ZipFile(path, 'r') as zip_file:
            namelist = zip_file.namelist()
            is_mcaddon = any(name.lower().endswith(".mcpack") for name in namelist)

            if is_mcaddon:
                plugin.logger.info(f"{filename} is an .mcaddon bundle. Processing inner packs.")
                with tempfile.TemporaryDirectory() as temp_dir:
                    zip_file.extractall(temp_dir)
                    for item in os.listdir(temp_dir):
                        if item.lower().endswith(".mcpack"):
                            inner_pack_path = os.path.join(temp_dir, item)
                            # Process each inner .mcpack file recursively
                            self._process_single_pack(inner_pack_path, plugin)
            else:
                plugin.logger.info(f"{filename} is a single archive. Scanning for packs inside.")
                # It's a regular .mcpack or a .zip with subfolders
                self._process_single_pack(path, plugin)
        
        plugin.logger.info(f"Finished processing addon from {filename}")

    def _process_single_pack(self, pack_path: str, plugin: Plugin):
        """
        Processes a single archive (.mcpack or .zip). It finds all manifest.json files within
        the archive and extracts each as a separate pack.
        """
        with ZipFile(pack_path, 'r') as zip_file:
            # NEW: First, find all manifest files in the zip to determine the packs.
            manifest_paths = [
                info.filename for info in zip_file.infolist() 
                if info.filename.lower().endswith("manifest.json") and not info.is_dir()
            ]

            if not manifest_paths:
                plugin.logger.warning(f"No 'manifest.json' found in {os.path.basename(pack_path)}. Skipping.")
                return

            plugin.logger.info(f"Found {len(manifest_paths)} pack(s) in {os.path.basename(pack_path)}.")

            # NEW: Process each found pack individually.
            for manifest_path in manifest_paths:
                self.__extract_pack_contents(manifest_path, zip_file, plugin)

    def __extract_pack_contents(self, manifest_path: str, zip_file: ZipFile, plugin: Plugin):
        """
        Extracts a single pack based on its manifest.json path within the zip file.
        The name of the extracted folder will be the name of the manifest's parent folder.
        """
        # CHANGED: The name of the pack is now derived from its folder in the zip.
        manifest_folder = os.path.dirname(manifest_path)
        pack_subfolder_name = os.path.basename(manifest_folder) if manifest_folder else os.path.splitext(os.path.basename(zip_file.filename))[0]

        with zip_file.open(manifest_path) as manifest_file:
            try:
                manifest = json.load(manifest_file)
                pack_type = get_pack_type(manifest)
            except (json.JSONDecodeError, KeyError) as e:
                plugin.logger.error(f"Failed to read or parse manifest '{manifest_path}': {e}")
                return

            if pack_type == PackType.Unknown:
                plugin.logger.error(f"Unknown pack type in '{manifest_path}', skipping.")
                return

            if pack_type == PackType.Bp:
                target_dir = PathProvider.behavior_packs()
            elif pack_type == PackType.Rp:
                target_dir = PathProvider.resource_packs()
            else:
                return

            plugin.logger.info(f"Extracting {pack_type.name} pack '{pack_subfolder_name}'...")

            # Extract all files belonging to this pack
            for member_info in zip_file.infolist():
                if member_info.filename.startswith(manifest_folder) and not member_info.is_dir():
                    # Create a path relative to the manifest's folder
                    relative_path = os.path.relpath(member_info.filename, manifest_folder)
                    
                    if ".." in relative_path.split(os.path.sep):
                        plugin.logger.warning(f"Skipping potentially unsafe path in zip: {member_info.filename}")
                        continue
                        
                    # CHANGED: Use pack_subfolder_name for the target directory name.
                    target_path = os.path.join(target_dir, pack_subfolder_name, relative_path)

                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    
                    with zip_file.open(member_info) as source, open(target_path, "wb") as target_file:
                        shutil.copyfileobj(source, target_file)

# Make the class instance available for import
addons_processor = AddonsProcessor()