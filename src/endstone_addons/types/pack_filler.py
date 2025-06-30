import os
import ujson as json
import tempfile
from zipfile import ZipFile, ZipInfo

from endstone_addons.tools.config_provider import set_configuration
from endstone_addons.tools.type_getter import get_pack_type
from endstone_addons.tools.zip_processor import process_zip
from endstone_addons.types.path_provider import PathProvider
from endstone_addons.types.pack_type import PackType

class PackFiller():
    def __init__(self):
        self.behavior_packs = []
        self.resource_packs = []
    
    def fill_packs(self):
        """
        Fills the behavior and resource pack lists by inspecting all addons.
        Handles both .mcpack and .mcaddon files.
        """
        for filename in os.listdir(PathProvider.addons()):
            # MODIFIED: Check for specific addon extensions
            if not filename.lower().endswith((".mcpack", ".mcaddon", ".zip")):
                continue
            
            path = os.path.join(PathProvider.addons(), filename)

            with ZipFile(path, 'r') as zip_file:
                is_mcaddon = any(name.lower().endswith(".mcpack") for name in zip_file.namelist())

                if is_mcaddon:
                    # For .mcaddon, extract to temp dir and process inner packs
                    with tempfile.TemporaryDirectory() as temp_dir:
                        zip_file.extractall(temp_dir)
                        for item in os.listdir(temp_dir):
                            if item.lower().endswith(".mcpack"):
                                inner_pack_path = os.path.join(temp_dir, item)
                                with ZipFile(inner_pack_path, 'r') as inner_zip:
                                    process_zip(inner_zip, self.__fill_pack_info, None)
                else:
                    # For .mcpack, process directly
                    process_zip(zip_file, self.__fill_pack_info, None)

        self.__save_pack_file("world_behavior_packs", self.behavior_packs)
        self.__save_pack_file("world_resource_packs", self.resource_packs)

    def __fill_pack_info(self, zip_info: ZipInfo, zip_file: ZipFile, plugin, name=None):
        """
        Reads a manifest file and adds its info to the behavior/resource pack lists.
        """
        with zip_file.open(zip_info.filename) as manifest_file:
            manifest = json.load(manifest_file)
            pack_type = get_pack_type(manifest)

            if pack_type == PackType.Unknown:
                return
            
            # Create a unique identifier to avoid duplicates
            pack_uuid = manifest["header"]["uuid"]
            
            info = {
                "pack_id": pack_uuid,
                "version": manifest["header"]["version"]
            }

            if pack_type == PackType.Bp:
                # Avoid adding duplicates
                if not any(p['pack_id'] == pack_uuid for p in self.behavior_packs):
                    self.behavior_packs.append(info)
            elif pack_type == PackType.Rp:
                # Avoid adding duplicates
                if not any(p['pack_id'] == pack_uuid for p in self.resource_packs):
                    self.resource_packs.append(info)

    def __save_pack_file(self, pack_file: str, packs: list):
        """Saves the pack list to the specified JSON file in the world folder."""
        # The original function is fine, just ensure we pass a list of dicts.
        set_configuration(pack_file, packs, PathProvider.world())

# Make the class instance available for import
pack_filler = PackFiller()