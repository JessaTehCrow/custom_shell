import os
from utils.shell import command

__desc__ = "Make, Hide or Unhide files"

def _hide_suggestion(self, args:list):
    search = ' '.join(args)
    files = [x for x in os.listdir() if os.path.isfile(x) and x.startswith(search)]

    space = '' if args else ' '
    if search in files:
        return
    elif files:
        return True, space+files[0][len(search):]

def _hide_highlight(self, args:list):
    search = ' '.join(args)
    files = [x for x in os.listdir() if os.path.isfile(x) and x.startswith(search)]
    
    color = '[R][U][BO]'
    if search in files:
        color = '[GR]'

    elif files:
        color = '[Y]'

    return [color]*len(args)

@command("Hide file or folder")
def hide(self, *path:str, silent:bool=False):
    "Make file or folder hidden"
    cprint = self.cprint.cprint

    __help__ = "[B]path [G]is the path to the file or folder from current directory"

    tohide = f"attrib +h {' '.join(path)}"
    if not os.path.isfile(' '.join(path)):
        cprint(f"[R]File not found")
        return 2

    os.system(tohide)
    if not silent:
        cprint(f'[GR]Succesfully hidden {" ".join(path)}')

def _unhide_suggestion(self, args:list):
    return _hide_suggestion(self, args)

def _unhide_highlight(self, args:list):
    return _hide_highlight(self, args)

@command("Unhide file or folder")
def unhide(self, *path:str, silent:bool=False):
    "Unhide a hidden folder or file"
    cprint = self.cprint.cprint
    
    __help__ = "[B]path [G]is the path to the file or folder from current directory"

    if not os.path.isfile(' '.join(path)):
        cprint(f"[R]File not found")
        return 2

    os.system(f"attrib -h {' '.join(path)}")
    if not silent:
        cprint(f"[GR]Succesfully unhid {' '.join(path)}")

@command("Make a new empty file or folder")
def new(self, type:str,name:str,hidden:bool=False):
    "Makes a new empty folder or file"
    cprint = self.cprint.cprint

    __help__ = "[B]Type [G] Either [P]folder [G]or [P]file\n[B]Name [G]Name of the folder/file\n[B]Hidden [P]True [G]or [P]False"

    if type.lower() == 'folder':
        os.mkdir(name)
        cprint(f'[GR]Succesfully made folder')

    elif type.lower() == 'file':
        with open(name,'w'):
            cprint(f'[GR]Succesfully made file')
    else:
        cprint(f"[R]Unknown type given.")
        return 1
        
    if hidden:
        hide(name,True)