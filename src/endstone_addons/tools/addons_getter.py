import os

from endstone.plugin import Plugin

from endstone_addons.types.storage import storage
from endstone_addons.tools.addon_downloader import download_addon, get_file_footprint
from endstone_addons.types.path_provider import PathProvider


def get_local_addons_to_add(plugin: Plugin):
        addons_paths = []
        for filename in os.listdir(PathProvider.addons()):

            if ".mc" not in filename and ".zip" not  in filename:
                continue

            if any(filename.startswith(addon["name"]) for addon in storage.conf.get("addons", [])):
                continue

            path = os.path.join(PathProvider.addons(), filename)
            footprint = get_file_footprint(path)

            if filename in storage.processed:
                if storage.processed.get(filename) == footprint:
                    plugin.logger.info(f"Skipping already processed addon {filename}")
                    continue
                plugin.logger.info(f"Addon {filename} has been modified, reprocessing.")
            else:
                plugin.logger.info(f"Processing new addon {filename}")

            storage.processed[filename] = footprint
            addons_paths.append(path)
        return addons_paths
    
def get_dedicated_addons_to_add(plugin: Plugin):
    addons_paths = []
    for addon in storage.conf.get("addons", []):
        local_path = download_addon(plugin, addon["url"], addon["name"])
        if local_path:
            addons_paths.append(local_path)
    return addons_paths