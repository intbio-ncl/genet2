import os
import json
import atexit

settings = "settings.json"

class SettingsManager:
    def __init__(self,graph):
        self._init_settings()
        atexit.register(self._save_settings)

    def _init_settings(self):
        if os.path.isfile(settings):
            with open(settings) as f:
                data = json.load(f)
            for k,v in data.items():
                setattr(self,k,v)

    def _save_settings(self):
        if os.path.isfile(settings):
            with open(settings) as f:
                data = json.load(f)
        else:
            data = {}
        
        for k,v in self.__dict__.items():
            if k.startswith("__"):
                continue
            data[k] = v

        with open(settings, 'w') as outfile:
            json.dump(data, outfile)

