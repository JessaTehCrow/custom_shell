import os
from utils.shell import command

__desc__ = "Change current directory"

def _main_suggestion(self, args:list):
    search = os.getcwd().replace('\\','/') + '/' + ' '.join(args)
    directory = '/'.join(search.split('/')[:-1])+"/"
    search = search.split('/')[-1] 

    if not os.path.isdir(directory):
        return 

    raw_paths = os.listdir(directory) + ['..', '.']
    dirs = [x for x in raw_paths if os.path.isdir(directory+x) and x.startswith(search)]

    space = '' if args else ' '
    if search in dirs:
        return 

    elif dirs:
        return True, space + dirs[0][len(search):]

def _main_highlight(self, args:list):
    search = os.getcwd().replace('\\','/') + '/' + ' '.join(args)
    if ':' in args:
        search = ' '.join(args)
        
    directory = '/'.join(search.split('/')[:-1])+"/"
    search = search.split('/')[-1] 

    if not os.path.isdir(directory):
        return 

    raw_paths = os.listdir(directory) + ['..', '.']
    dirs = [x for x in raw_paths if os.path.isdir(directory+x) and x.startswith(search)]
    
    color = '[R][U][BO]'
    if search in dirs or not search:
        color = '[GR]'

    elif dirs:
        color = '[Y]'

    return [color]*len(args)

@command("Changes current directory")
def main(*path:str):
    "Change current directory"
    path = ' '.join(path)
    if os.path.isdir(path):
        os.chdir(path)
    else:
        print("Directory not found. Does it exist?")
        return 2