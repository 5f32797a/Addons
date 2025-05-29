import os
from zipfile import ZipFile, ZipInfo
import ujson as json

from endstone_addons.tools.config_provider import get_configuration, set_configuration
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
            if ".mc" not in filename and ".zip" not in filename:
                continue
            
            path = os.path.join(PathProvider.addons(), filename)

            with ZipFile(path, 'r') as zip:
                process_zip(zip, self.__fill_pack, None)


        self.__save_pack_file("world_behavior_packs", self.behavior_packs)
        self.__save_pack_file("world_resource_packs", self.resource_packs)


    def __fill_pack(self, zip_info: ZipInfo, zip: ZipFile, plugin, name):
        with zip.open(zip_info.filename) as manifest_file:
            manifest = json.load(manifest_file)
            type = get_pack_type(manifest)

            if type == PackType.Unknown:
                return
            
            info = {
                "pack_id": manifest["header"]["uuid"],
                "version": manifest["header"]["version"]
            }

            if type == PackType.Bp:
                self.behavior_packs.append(info)
            elif type == PackType.Rp:
                self.resource_packs.append(info)

    def __save_pack_file(self, pack_file: str, pack: list):
        set_configuration(pack_file, pack, PathProvider.world())

pack_filler = PackFiller()