import endstone_addons.tools.config_provider as conf
from endstone_addons.types.path_provider import PathProvider

class Storage:

    def __init__(self):
        self.conf = conf.get_configuration("config")
        self.processed = conf.get_configuration("processed", PathProvider.addons())

    def save_processed(self):
        conf.set_configuration("processed", self.processed, PathProvider.addons())

storage: Storage = Storage()