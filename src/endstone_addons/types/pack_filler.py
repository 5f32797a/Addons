import os
import ujson as json
from zipfile import ZipFile, ZipInfo, is_zipfile, BadZipFile

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
        for filename in os.listdir(PathProvider.addons()):
            if not filename.lower().endswith((".mcpack", ".mcaddon", ".zip")):
                continue
            
            path = os.path.join(PathProvider.addons(), filename)
            if not is_zipfile(path):
                continue
            
            try:
                with ZipFile(path, 'r') as zip_file:
                    process_zip(zip_file, self.__fill_pack_info, None, os.path.splitext(filename)[0])
            except (BadZipFile, Exception):
                continue # Silently ignore corrupted files for the filler

        self.__save_pack_file("world_behavior_packs", self.behavior_packs)
        self.__save_pack_file("world_resource_packs", self.resource_packs)

    def __fill_pack_info(self, zip_info: ZipInfo, zip_file: ZipFile, plugin, name=None):
        try:
            with zip_file.open(zip_info.filename) as manifest_file:
                manifest = json.load(manifest_file)
            
            pack_type = get_pack_type(manifest)
            if pack_type == PackType.Unknown or "header" not in manifest or "uuid" not in manifest["header"]:
                return

            pack_uuid = manifest["header"]["uuid"]
            info = {"pack_id": pack_uuid, "version": manifest["header"].get("version", [1, 0, 0])}
            
            if pack_type == PackType.Bp and not any(p['pack_id'] == pack_uuid for p in self.behavior_packs):
                self.behavior_packs.append(info)
            elif pack_type == PackType.Rp and not any(p['pack_id'] == pack_uuid for p in self.resource_packs):
                self.resource_packs.append(info)
        except (json.JSONDecodeError, UnicodeDecodeError, KeyError):
            return # Silently ignore invalid manifests

    def __save_pack_file(self, pack_file: str, packs: list):
        set_configuration(pack_file, packs, PathProvider.world())

pack_filler = PackFiller()