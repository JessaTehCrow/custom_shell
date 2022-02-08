import os, sys

import importlib

from utils import loader
from utils.shell import command

__desc__ = "Reload or refresh commands"

@command("Reloads all functions and commands")
def refresh(self):
    "Reloads all functions and commands"
    cdir = os.getcwd()
    os.chdir(sys.path[0])

    loader.refresh()
    
    self._suggestion._update_data()
    self._highlight._update_data()

    os.chdir(cdir)

def _reload_suggestion(self, args:list):
    search = ' '.join(args)
    modules = [x for x in list(self.commands)[1:] if x.startswith(search)]

    space = '' if args else ' '
    if search in modules:
        return False, ''

    elif modules:
        return True, space + modules[0][len(search):]

def _reload_highlight(self, args:list):
    if not args:
        return

    search = ' '.join(args[:1])
    modules = [x for x in list(self.commands)[1:] if x.startswith(search)]

    color = '[R][U][BO]'
    if search in modules:
        color = '[P]'

    elif modules:
        color = '[Y]'

    args[0] = color 
    args[1:] = [f'[R][U][BO]' for x in args[1:]]
    
    return args

@command("Reload module")
def reload(self, module:str):
    cprint = self.cprint.cprint
    
    cdir = os.getcwd()
    os.chdir(sys.path[0])

    if not module in self.commands:
        cprint(f"[R]Module not found.")
        os.chdir(cdir)
        return 2

    desc = self.commands[module]['description']
    long_desc = self.commands[module]['long_description']
    self.commands[module] = {"description":desc, "long_description":long_desc}

    importlib.reload(self.raw_import[module])

    os.chdir(cdir)


@command("Restart shell completely")
def restart(self):
    path = sys.path[0] + '/main.py'

    os.execl(sys.executable, 'python', path)