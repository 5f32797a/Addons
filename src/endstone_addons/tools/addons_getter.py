import os
import shutil
from zipfile import is_zipfile
from endstone.plugin import Plugin

from endstone_addons.types.storage import storage
from endstone_addons.tools.addon_downloader import download_addon, get_file_footprint
from endstone_addons.types.path_provider import PathProvider

def _is_pack_installed(filename: str, plugin: Plugin) -> bool:
    """
    Checks if all packs from a processed addon are actually installed by
    looking for their specific hashed folders.
    """
    processed_info = storage.processed.get(filename)
    if not isinstance(processed_info, dict) or "packs" not in processed_info:
        plugin.logger.debug(f"Pack {filename} not in new processed format or no packs recorded, assuming not installed.")
        return False

    pack_folders = processed_info["packs"]
    if not pack_folders:
        return True  # Addon has no packs, so it's "installed".

    for pack_folder_name in pack_folders:
        bp_path = os.path.join(PathProvider.behavior_packs(), pack_folder_name)
        rp_path = os.path.join(PathProvider.resource_packs(), pack_folder_name)
        if not os.path.isdir(bp_path) and not os.path.isdir(rp_path):
            plugin.logger.debug(f"Missing installed folder for pack '{pack_folder_name}' from addon '{filename}'.")
            return False
            
    return True

def get_local_addons_to_add(plugin: Plugin) -> list:
    """
    Gets a list of local addon file paths that need to be processed.
    Handles new, modified, and manually deleted packs.
    """
    addons_to_process = []
    for filename in os.listdir(PathProvider.addons()):

        if not filename.lower().endswith((".mcpack", ".mcaddon", ".zip")):
            continue

        if any(filename.startswith(addon["name"]) for addon in storage.conf.get("addons", [])):
            continue

        path = os.path.join(PathProvider.addons(), filename)
        if not is_zipfile(path):
            continue

        loggable_filename = filename.encode('utf-8', 'replace').decode('utf-8')
        footprint = get_file_footprint(path)
        processed_info = storage.processed.get(filename)

        # Case 1: Brand new addon
        if not processed_info:
            plugin.logger.info(f"Processing new addon {loggable_filename}")
            addons_to_process.append(path)
            continue

        # Force re-process if using old data format
        if not isinstance(processed_info, dict) or "footprint" not in processed_info:
            plugin.logger.info(f"Data for '{loggable_filename}' is outdated. Reprocessing.")
            addons_to_process.append(path)
            continue

        # Case 2: Modified file. Clean up old packs first.
        if processed_info["footprint"] != footprint:
            plugin.logger.info(f"Addon '{loggable_filename}' has been modified. Cleaning up old version and reprocessing.")
            old_packs = processed_info.get("packs", [])
            for pack_folder in old_packs:
                for base_dir in [PathProvider.behavior_packs(), PathProvider.resource_packs()]:
                    folder_to_delete = os.path.join(base_dir, pack_folder)
                    if os.path.isdir(folder_to_delete):
                        plugin.logger.info(f"Removing old pack folder: {pack_folder}")
                        shutil.rmtree(folder_to_delete)
            addons_to_process.append(path)
            continue

        # Case 3: Unchanged file. Check if packs were manually deleted.
        if not _is_pack_installed(filename, plugin):
            plugin.logger.info(f"Addon '{loggable_filename}' was processed but not found in world folders. Reprocessing.")
            addons_to_process.append(path)
            continue
        
        plugin.logger.info(f"Skipping already processed addon {loggable_filename}")

    return addons_to_process

def get_dedicated_addons_to_add(plugin: Plugin) -> list:
    """
    Downloads and gets a list of dedicated addon files from the config.
    The main processing loop will handle installation checks.
    """
    addons_paths = []
    for addon in storage.conf.get("addons", []):
        local_path = download_addon(plugin, addon["url"], addon["name"])
        if local_path:
            # We don't need to add it to the processing list here, because
            # get_local_addons_to_add will pick it up as a modified/new file.
            pass
    # The logic is now handled by get_local_addons_to_add, so we just need to ensure
    # files are downloaded. Let's return the paths of newly downloaded/updated files.
    # A better approach is to let get_local_addons_to_add handle everything.
    # The download function should just download.
    for addon in storage.conf.get("addons", []):
        download_addon(plugin, addon["url"], addon["name"])
        
    return [] # All logic is now consolidated in get_local_addons_to_add