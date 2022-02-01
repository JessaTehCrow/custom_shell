import os, sys

__desc__ = "Reload or refresh commands"

def refresh(self):
    "Reloads all functions and commands"
    cdir = os.getcwd()
    os.chdir(sys.path[0])

    for x in self.modules:  
        sys.modules.pop(x)

    toload = ['base','custom']

    self.modules = []
    self._load_functions(toload)
    
    for x in self.events:
        self.events[x] = []

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

def reload(self,module:str):
    cprint = self.cprint.cprint
    
    "Reload module"
    cdir = os.getcwd()
    os.chdir(sys.path[0])

    if not module in self.commands:
        cprint(f"[R]Module not found.")
        os.chdir(cdir)
        return 2
    
    pyloc = [x for x in self.modules if x.endswith("."+module)][0]
    loc = '/'.join(pyloc.split('.')[:-1])+'/'

    sys.modules.pop(pyloc)
    self.modules.remove(pyloc)
    self.commands.pop(module)
    self.load_function(module,loc)

    os.chdir(cdir)
