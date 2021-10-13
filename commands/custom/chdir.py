import os

__desc__ = "A quick way to save and go to directories on your computer"
__long_desc__ = """[R]chdir[P]

chdir is a easy way to save and go to directories. Saving huge amounts of time over the long run."""

cprint = None

def on_load(self):
    global cprint
    cprint =  self.cprint

def on_shell_ready(self):
    global dirs
    self.chdirs = self.loader.load({},"directories")

def _get_dir(self,name):
    if not name in self.chdirs:
        cprint.cprint(f'[G]{name} [R]Not found')
        return False
    return self.chdirs[name]

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

def save(self,*name:str):
    "Save current directory in chdir"
    __help__ = "[B]Name[G] Saved name for current directory"
    name = ' '.join(name)

    directory = os.getcwd().replace('\\','/')
    cprint.cprint(f"[GR]Saving [B]{directory} [GR]with name [B]{name}")
    self.chdirs[name] = directory

    self.loader.save(self.chdirs,"directories")

def remove(self,*name:str):
    "Remove saved directory"
    __help__ = "[B]Name[G] Name of a saved directory"
    name = ' '.join(name)

    if _get_dir(self,name):
        del self.chdirs[name]
        self.loader.save(self.chdirs,"directories")
    else:
        return 2

def start(self,*name:str):
    "Open directory with file exporer"
    __help__ = "[B]Name[G] Name of a saved directory"
    name = ' '.join(name)
    directory = _get_dir(self,name)
    if directory:
        os.system(f'start {directory}')
    else:
        return 2