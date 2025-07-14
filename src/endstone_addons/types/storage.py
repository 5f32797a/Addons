import endstone_addons.tools.config_provider as conf
from endstone_addons.types.path_provider import PathProvider
import os

class Storage:

    def __init__(self):
        self.conf = {}
        self.processed = {}

    def init(self):
        self.conf = conf.get_configuration("config")
        
        config_updated = False
        if not self.conf.get("world"):
            worlds_path = f"{os.getcwd()}/worlds/"
            if os.path.exists(worlds_path):
                worlds = [d for d in os.listdir(worlds_path) if os.path.isdir(os.path.join(worlds_path, d))]
                if worlds:
                    self.conf["world"] = worlds[0]
                    config_updated = True

        if "restart_on_update" not in self.conf:
            self.conf["restart_on_update"] = True
            config_updated = True

        if config_updated:
            conf.set_configuration("config", self.conf)

        self.processed = conf.get_configuration("processed", PathProvider.addons())

    def save_processed(self):
        conf.set_configuration("processed", self.processed, PathProvider.addons())

storage: Storage = Storage()