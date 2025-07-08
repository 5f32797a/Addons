import os

from endstone import ColorFormat as CF
from endstone.plugin import Plugin

from endstone_addons.types.storage import storage
from endstone_addons.types.path_provider import PathProvider
from endstone_addons.tools.addons_getter import get_local_addons_to_add, get_dedicated_addons_to_add
from endstone_addons.tools.addon_downloader import get_file_footprint # Import needed function

from endstone_addons.types.addons_processor import addons_processor
from endstone_addons.types.pack_filler import pack_filler
from endstone_addons.types.cleaner import cleaner

class AddonsPlugin(Plugin):
    version = "0.1.2"
    api_version = "0.6"

    def on_load(self):
        super().on_load()

        storage.init()

        self.logger.info(f"\n{CF.AQUA}Addons processing started...\n")
        os.makedirs(PathProvider.addons(), exist_ok=True)
        os.makedirs(PathProvider.behavior_packs(), exist_ok=True)
        os.makedirs(PathProvider.resource_packs(), exist_ok=True)

        # Download dedicated addons first, so get_local_addons_to_add can see them
        get_dedicated_addons_to_add(self)
        
        # Get a list of all addons that require processing
        addons_paths_to_process = get_local_addons_to_add(self)

        # Process the addons and get a map of what was extracted
        extracted_map = addons_processor.process_addons(addons_paths_to_process, self)

        # Update the processed storage with the results
        for path, pack_names in extracted_map.items():
            filename = os.path.basename(path)
            footprint = get_file_footprint(path)
            storage.processed[filename] = {
                "footprint": footprint,
                "packs": pack_names
            }

        # Clean up any packs from fully deleted addon files
        cleaner.clean(self)
        
        # Update world packs configuration
        pack_filler.fill_packs()

        storage.save_processed()
        self.logger.info(f"\n{CF.GREEN}Addons processing completed.\n")

        # Restart server only if addons were actually changed
        if len(addons_paths_to_process) > 0:
            self.logger.info("Addon changes were detected. Shutting down server for changes to take effect.")
            self.server.shutdown()