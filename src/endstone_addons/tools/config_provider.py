import os
import json

configuration_path = f"{os.getcwd()}/plugins/configuration/addons/"

def get_configuration(file: str, path: str | None = None) -> dict | list:
    target_path = path or configuration_path
    os.makedirs(target_path, exist_ok=True)
    file_path = os.path.join(target_path, f"{file}.json")
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as jsonFile:
            json.dump({}, jsonFile, ensure_ascii=False, indent=4)
        return {}
    with open(file_path, "r", encoding="utf-8") as jsonFile:
        return json.load(jsonFile)
    
def set_configuration(file: str, data: dict | list, path: str | None = None) -> None:
    target_path = path or configuration_path
    os.makedirs(target_path, exist_ok=True)
    file_path = os.path.join(target_path, f"{file}.json")
    with open(file_path, "w", encoding="utf-8") as jsonFile:
        json.dump(data, jsonFile, ensure_ascii=False, indent=4)