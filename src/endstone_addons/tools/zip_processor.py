import os
import re
import hashlib
from zipfile import ZipFile, ZipInfo, is_zipfile, BadZipFile

def _sanitize_name(name: str) -> str:
    """Cleans up a string to be used as a valid folder name."""
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'[\s.]+', '_', name)
    return name

def get_hashed_pack_name(base_name: str, manifest_internal_path: str) -> str:
    """Generates a unique, short, and hashed folder name for a pack."""
    sanitized_base = _sanitize_name(base_name)
    max_base_len = 30
    if len(sanitized_base) > max_base_len:
        sanitized_base = sanitized_base[:max_base_len]
    
    pack_sub_folder = os.path.dirname(manifest_internal_path.replace("\\", "/"))
    path_hash = hashlib.md5((base_name + pack_sub_folder).encode()).hexdigest()[:8] # Use base_name for more uniqueness
    
    final_pack_name = f"{sanitized_base}_{path_hash}"
    return final_pack_name

def process_zip_recursive(zip_file: ZipFile, func, plugin, base_name: str):
    """
    Recursively finds ALL valid manifest.json files, even in nested zips,
    and calls the function for each.
    """
    manifests_found_in_this_level = False
    
    # --- Pass 1: Find manifests at the current level ---
    for zip_info in zip_file.infolist():
        filename = zip_info.filename.replace("\\", "/")
        if filename.lower().endswith("manifest.json") and not filename.startswith("__MACOSX/"):
            manifests_found_in_this_level = True
            final_pack_name = get_hashed_pack_name(base_name, zip_info.filename)
            func(zip_info, zip_file, plugin, final_pack_name)

    # --- Pass 2: If no manifests found, look for nested zips ---
    if not manifests_found_in_this_level:
        for zip_info in zip_file.infolist():
            filename = zip_info.filename
            if filename.lower().endswith((".mcpack", ".mcaddon", ".zip")) and not zip_info.is_dir():
                plugin.logger.debug(f"Found nested archive: '{filename}' inside '{base_name}'. Processing recursively.")
                try:
                    # Read the nested zip into memory and process it
                    with zip_file.open(filename) as nested_zip_file:
                        from io import BytesIO
                        nested_zip_stream = BytesIO(nested_zip_file.read())
                        with ZipFile(nested_zip_stream, 'r') as nested_zf:
                            # The base name for the nested pack should be derived from the nested zip's name
                            nested_base_name = os.path.splitext(os.path.basename(filename))[0]
                            process_zip_recursive(nested_zf, func, plugin, nested_base_name)
                except (BadZipFile, Exception) as e:
                    plugin.logger.warning(f"Could not process nested archive '{filename}': {e}")

# This will be the main entry point now, replacing the old process_zip
process_zip = process_zip_recursive