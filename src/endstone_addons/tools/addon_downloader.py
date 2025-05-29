import os

from endstone.plugin import Plugin
import requests

from endstone_addons.types.path_provider import PathProvider
from endstone_addons.types.storage import storage

def get_file_footprint(url: str) -> str:
    if url.startswith("http://") or url.startswith("https://"):
        response = requests.head(url)
        if response.status_code == 200:
            return str(response.headers.get('etag', ''))
        return ""
    return str(os.path.getmtime(url))    

def download_addon(plugin: Plugin, url: str, name: str) -> str:
    response = requests.head(url)
    if response.status_code != 200:
        plugin.logger.error(f"Failed to download {url}: Status code {response.status_code}")
        return None
    
    extension = response.headers.get('content-type', '').split('/')[-1]

    file = f"{name}.{extension}"
    file_path = os.path.join(PathProvider.addons(), file)

    footprint = get_file_footprint(url)

    if storage.processed.get(file) == footprint:
        plugin.logger.info(f"Skipping already downloaded addon {file}")
        return None
    
    storage.processed[file] = footprint
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        plugin.logger.error(f"Failed to download {url}: Status code {response.status_code}")
        return None
    
    return file_path
