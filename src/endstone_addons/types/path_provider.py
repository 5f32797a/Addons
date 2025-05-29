import os

class PathProvider:

    @staticmethod
    def addons() -> str:
        return f"{os.getcwd()}/addons/"
    
    @staticmethod
    def world() -> str:
        from endstone_addons.types.storage import storage
        return f"{os.getcwd()}/worlds/{storage.conf['world']}"
    
    @staticmethod
    def behavior_packs() -> str:
        from endstone_addons.types.storage import storage
        return f"{os.getcwd()}/worlds/{storage.conf['world']}/behavior_packs"
    
    @staticmethod
    def resource_packs() -> str:
        from endstone_addons.types.storage import storage
        return f"{os.getcwd()}/worlds/{storage.conf['world']}/resource_packs"
        