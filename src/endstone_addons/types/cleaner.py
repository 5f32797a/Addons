import os
import shutil

from endstone.plugin import Plugin
from endstone_addons.types.storage import storage
from endstone_addons.types.path_provider import PathProvider

class Cleaner:
    def clean(self, plugin: Plugin):
        """
        Cleans up installed packs for which the source addon file has been deleted.
        """
        processed_filenames = list(storage.processed.keys())

        for filename in processed_filenames:
            addon_path = os.path.join(PathProvider.addons(), filename)
            
            if not os.path.exists(addon_path):
                loggable_filename = filename.encode('utf-8', 'replace').decode('utf-8')
                plugin.logger.info(f"Addon file '{loggable_filename}' was removed. Cleaning up installed packs.")
                processed_info = storage.processed.get(filename)

                if isinstance(processed_info, dict) and "packs" in processed_info:
                    for pack_folder in processed_info["packs"]:
                        # Check both directories and remove the hashed folder
                        rp_path = os.path.join(PathProvider.resource_packs(), pack_folder)
                        bp_path = os.path.join(PathProvider.behavior_packs(), pack_folder)
                        
                        if os.path.isdir(rp_path):
                            plugin.logger.info(f"Removing resource pack folder '{pack_folder}'")
                            shutil.rmtree(rp_path)
                        if os.path.isdir(bp_path):
                            plugin.logger.info(f"Removing behavior pack folder '{pack_folder}'")
                            shutil.rmtree(bp_path)
                
                del storage.processed[filename]

cleaner = Cleaner()