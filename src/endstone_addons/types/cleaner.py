import os
import shutil

from endstone.plugin import Plugin
from endstone_addons.types.storage import storage
from endstone_addons.types.path_provider import PathProvider

class Cleaner:
    def clean(self, plugin: Plugin):
        for processed in storage.processed:
            folder_name = os.path.splitext(processed)[0]
            path = os.path.join(PathProvider.addons(), processed)
            if not os.path.exists(path):
                resorce_pack_path = os.path.join(PathProvider.resource_packs(), folder_name)
                behavior_pack_path = os.path.join(PathProvider.behavior_packs(), folder_name)

                if os.path.exists(resorce_pack_path):
                    plugin.logger.info(f"Removing resource pack {processed}")
                    shutil.rmtree(resorce_pack_path)
                if os.path.exists(behavior_pack_path):
                    plugin.logger.info(f"Removing behavior pack {processed}")
                    shutil.rmtree(behavior_pack_path)

cleaner = Cleaner()