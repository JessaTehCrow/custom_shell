import os
from utils.shell import command, event

__desc__ = "A quick way to save and go to directories on your computer"
__long_desc__ = """[R]chdir[P]

chdir is a easy way to save and go to directories. Saving huge amounts of time over the long run."""

cprint = None

@event("on_load")
def on_load(self):
    global cprint
    cprint =  self.cprint

@event("on_shell_ready")
def on_shell_ready(self):
    global dirs
    self.chdirs = self.loader.load({},"directories")

def _get_dir(self, name):
    if not name in self.chdirs:
        cprint.cprint(f'[G]{name} [R]Not found')
        return False
    return self.chdirs[name]


def _main_suggestion(self, args:list):
    name = ' '.join(args)
    dirs = [x for x in self.chdirs if x.startswith(name)]

    space = '' if args else ' '
    if dirs:
        return True, space + dirs[0][len(name):]

def _main_highlight(self, args:list):
    name = ' '.join(args)
    dirs = [x for x in self.chdirs if x.startswith(name)]
    
    color = '[R][U][BO]'
    if name in dirs:
        color = "[GR]"
    elif dirs:
        color = '[Y]'

    return [color]*len(args)

@command("List directories or go to directory",
"""[B]name[G] is one of the previously saved directory names.
Call without arguments to list available directories
""")
def main(self,*name:str):
    "List directories or go to directory"
    cols = {
        "name":"[GR]",
        "directory":"[P]"
    }
    cols = [*self.loader.load(cols,"colors").values()]

    if not name:
        toprint = [*self.chdirs.items()]
        titles = ["Name","Directory"]
        title_col = '[B]'
        print()
        cprint.c_tabulate(toprint,titles,cols=cols,title_cols=title_col,sort="Name")
        print()
        return 0

    name = ' '.join(name)
    directory = _get_dir(self,name)
    if directory:
        cprint.cprint(f'\n[GR]Going to [B]{name} [G]({directory})\n')
        os.chdir(directory)

@command("Save current directory to chdir", "[B]Name[G] Saved name for current directory")
def save(self,*name:str):
    name = ' '.join(name)

    directory = os.getcwd().replace('\\','/')
    cprint.cprint(f"[GR]Saving [B]{directory} [GR]with name [B]{name}")
    self.chdirs[name] = directory

    self.loader.save(self.chdirs,"directories")


def _remove_highlight(self, args:list):
    return _main_highlight(self, args)

def _remove_suggestion(self, args:list):
    return _main_suggestion(self, args)

@command("Remove saved directory", "[B]Name[G] Name of a saved directory")
def remove(self,*name:str):
    name = ' '.join(name)

    if _get_dir(self,name):
        del self.chdirs[name]
        self.loader.save(self.chdirs,"directories")
    else:
        return 2


def _start_highlight(self, args:list):
    return _main_highlight(self, args)

def _start_suggestion(self, args:list):
    return _main_suggestion(self, args)

@command("Open directory with file explorer", "[B]Name[G] Name a saved directory")
def start(self,*name:str):
    name = ' '.join(name)
    directory = _get_dir(self,name)
    if directory:
        os.system(f'start {directory}')
    else:
        return 2