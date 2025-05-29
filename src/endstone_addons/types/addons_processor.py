import os
import ujson as json

from zipfile import ZipFile, ZipInfo
from endstone.plugin import Plugin
from endstone_addons.tools.type_getter import get_pack_type
from endstone_addons.types.pack_type import PackType
from endstone_addons.tools.zip_processor import process_zip
from endstone_addons.types.path_provider import PathProvider


class AddonsProcessor:
    def process_addons(self, addons_paths: list, plugin: Plugin):
        for path in addons_paths:
            filename = os.path.basename(path)

            with ZipFile(path, 'r') as zip:
                process_zip(zip, self.__extract_addon, plugin, os.path.splitext(filename)[0])
                plugin.logger.info(f"Processed addon {filename}")

    def __extract_addon(self, zip_info: ZipInfo, zip: ZipFile, plugin: Plugin, name: str):
        manifest_folder = os.path.dirname(zip_info.filename)
        with zip.open(zip_info.filename) as manifest_file:
            manifest = json.load(manifest_file)
            type = get_pack_type(manifest)

            if type == PackType.Unknown:
                plugin.logger.error(f"Unknown pack type for {zip_info.filename}, skipping.")
                return

            if type == PackType.Bp:
                target_dir = PathProvider.behavior_packs()
            elif type == PackType.Rp:
                target_dir = PathProvider.resource_packs()

            for member in zip.namelist():
                if member.startswith(manifest_folder + "/") and not member.endswith("/"):

                    relative_path = os.path.relpath(member, manifest_folder).encode('ascii', 'replace').decode('ascii')
                    target_path = os.path.join(target_dir, name, relative_path).encode('ascii', 'replace').decode('ascii')

                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with zip.open(member) as source, open(target_path, "wb") as target_file:
                        target_file.write(source.read())

addons_processor = AddonsProcessor()