import os, sys

import traceback
import importlib

from utils.shell import shell
from sys import stdout as std
from cprint import cconvert, cprint


paths = [
    'commands/base',
    'commands/custom'
]


def load():
    "Load all modules into shell"

    for directory in paths:
        files = [file[:-3] for file in os.listdir(directory) if file.endswith('.py')]
        pydir = directory.replace('/', '.')

        for module in files:
            pyname = f"{pydir}.{module}"
 
            try:
                shell.commands[module] = {}

                module_lib = importlib.import_module(pyname)
                shell.raw_import[module] = module_lib
                shell.modules.append(pyname)

                desc, long_desc = '', ''
                if hasattr(module_lib, "__desc__"):
                    desc = module_lib.__desc__

                if hasattr(module_lib, "__long_desc__"):
                    long_desc = module_lib.__long_desc__
                
                shell.commands[module]['description'] = desc
                shell.commands[module]['long_description'] = long_desc

                shell._do_event("on_ready")
            except:
                std.write(cconvert(f"\r[R]Error importing {pyname}:\n\n{traceback.format_exc()}"))
                std.flush()
                continue

            std.write(cconvert(f"\r[GR]Successfully imported the [G]{module}[GR] module\n"))
            std.flush()

    shell._do_event("on_shell_ready")


# I'll worry about this later i guess    
def refresh():
    "Refresh all modules"
    self = shell

    for x in shell.modules:
        sys.modules.pop(x)
    
    self.commands = {}  
    self.raw_import = {}
    self.modules = []
    self.events = {
        "on_load":[],
        "on_shell_ready":[],
        "on_ready":[]
    }
    self.after_load = []

    load()