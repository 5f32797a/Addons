from zipfile import ZipFile

def process_zip(zip: ZipFile, func, plugin, name: str = None, ):
    for zip_info in zip.infolist():
        if zip_info.filename.endswith("manifest.json") and zip_info.filename.count("/") >= 1:
            func(zip_info, zip, plugin,name)