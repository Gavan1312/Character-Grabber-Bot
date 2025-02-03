'''import random
import sys
import time
from Grabber import *
from functools import wraps
from telegram import Update
from Grabber.utils import * 
from Grabber.modules.watchers import *

sudb = db.sudo
devb = db.dev 
app = Grabberu

dev_users = {880926547}

LOAD = []
NO_LOAD = []


def __list_all_modules_UploaderPanel():
    import glob
    from os.path import basename, dirname, isfile

    # mod_paths = glob.glob(dirname(__file__) + "/*.py")
    # all_modules = [
    #     basename(f)[:-3]
    #     for f in mod_paths
    #     if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
    # ]
    mod_paths = glob.glob(dirname(__file__) + "/**/*.py", recursive=True)
    all_modules = [
        os.path.relpath(f, dirname(__file__)).replace(os.sep, ".")[:-3]
        for f in mod_paths
        if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
    ]

    if LOAD or NO_LOAD:
        to_load = LOAD
        if to_load:
            if not all(
                any(mod == module_name for module_name in all_modules)
                for mod in to_load
            ):
                print("Invalid loadorder names, Quitting...")
                quit(1)

            all_modules = sorted(set(all_modules) - set(to_load))
            to_load = list(all_modules) + to_load

        else:
            to_load = all_modules

        if NO_LOAD:
            print("Not loading: {}".format(NO_LOAD))
            return [item for item in to_load if item not in NO_LOAD]

        return to_load

    return all_modules

ALL_MODULES_UploaderPanel = __list_all_modules_UploaderPanel()
print("Modules to load: %s", str(ALL_MODULES_UploaderPanel))
__all__ = ALL_MODULES_UploaderPanel + ["ALL_MODULES_UploaderPanel"]
'''