import os

from endstone import ColorFormat as CF
from endstone.plugin import Plugin

from endstone_addons.types.storage import storage
from endstone_addons.types.path_provider import PathProvider
from endstone_addons.tools.addons_getter import get_local_addons_to_add, get_dedicated_addons_to_add

from endstone_addons.types.addons_processor import addons_processor
from endstone_addons.types.pack_filler import pack_filler
from endstone_addons.types.cleaner import cleaner

class AddonsPlugin(Plugin):
    version = "0.1.0"
    api_version = "0.6"

    behavior_packs = []
    resource_packs = []

    def on_load(self):
        super().on_load()

        self.logger.info(f"\n{CF.AQUA}Addons processing started...\n")
        os.makedirs(PathProvider.addons(), exist_ok=True)
        os.makedirs(PathProvider.behavior_packs(), exist_ok=True)
        os.makedirs(PathProvider.resource_packs(), exist_ok=True)

        addons_paths = get_local_addons_to_add(self)
        addons_paths += get_dedicated_addons_to_add(self)

        addons_processor.process_addons(addons_paths, self)
        cleaner.clean(self)
        pack_filler.fill_packs()

        storage.save_processed()
        self.logger.info(f"\n{CF.GREEN}Addons processing completed.\n")

        if len(addons_paths) > 0:
            self.server.shutdown()