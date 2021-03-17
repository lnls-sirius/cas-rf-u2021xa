import logging
import json

logger = logging.getLogger(__name__)
CONFIG_FILE = "./settings/config.json"


class ConfigManager:
    def __init__(self):
        self.unit = "DBM"
        self.freq = "500000000Hz"
        self.gain = 74.3
        self.trac_time = 0.41
        self.trac_time_new = self.trac_time

    def update_trac_time(self):
        self.trac_time = self.trac_time_new

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                self.unit = config["unit"]
                self.gain = config["gain"]
                self.freq = config["freq"]
                self.trac_time = config["trac_time"]
                self.trac_time_new = self.trac_time
                logger.info("Loaded '{}' from config.json".format(config))
        except:
            logger.exception(
                "Failed to load from config.json, falling back to defaults"
            )
            self.unit = "DBM"
            self.freq = "500000000Hz"
            self.gain = 74.3
            self.trac_time = 0.41
            self.trac_time_new = self.trac_time

            logger.info("Attempting to dump the fresh")
            self.dump_config()

    def dump_config(self):
        try:
            config = {
                "gain": self.gain,
                "freq": self.freq,
                "trac_time": self.trac_time,
                "unit": self.unit,
            }

            with open(CONFIG_FILE, "w+") as f:
                json.dump(config, f)
            logger.info("Update config.json")
        except:
            logger.exception("Failed to dump config")
