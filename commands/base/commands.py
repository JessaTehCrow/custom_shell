from utils.utils import * # type: ignore
from utils.cprint import *
import os,sys,re

if os.name == 'nt':
    try:
        import win32api, win32con
        succes = True
    except:
        print("Unable to load script. (missing 'pypiwin32', can be installed with 'pip install pypiwin32')")

colors = {
    "file":"[Y]",
    "directory":"[GR]",
    "hidden_file":"[L]",
    "hidden_directory":"[R]",
    "executable":"[B]"
}

class node:
    def __init__(self,name):
        self.name = name
        self.hidden = self.get_hidden()
        self.type = self.get_type()
        self.executable = self.get_executable()
        self.color = colors['executable'] if self.executable else colors[self.type]

    def get_type(self):
        new_type = "directory" if os.path.exists(self.name+"/") else "file"
        new_type = new_type if not self.hidden else "hidden_"+new_type
        return new_type

    def get_hidden(self):
        if os.name == 'nt':
            attribute = win32api.GetFileAttributes(self.name)
            return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
        else:
            return self.name.startswith('.')

    def get_executable(self):
        if "file" in self.type and os.name != "nt":
            return os.access(self.name, os.X_OK)

        return False

def c():
    "Clears screen"
    if is_windows(): # type: ignore
        os.system("cls")  
    else:            
        os.system("clear")
    
def clear():
    "Clears screen"
    c()

def exit():
    "Closes shell"
    quit()

def help(self,arg1:str=None,arg2:str=None):
    "Shows help for function"
    __help__ = "[B]arg1 [G]is either a [L]buildin command[G], or a [GR]module[G].\nIf [B]arg2[G] is used, [B]arg1 [G]needs to be a [GR]module[G], and [B]arg2 [G]a [L]Command[G] within the module."
    print()

    title = "[B]"
    def print_funcs(array, long_desc:str = None):
        if long_desc: cprint("[P]" + long_desc + '\n')

        funcs = []
        for x in array: 
            funcs.append([x.name,f"{x.desc or '[BL]'}"])
        cols = [["[L]","[B]"],["[R]",'[P]']]
        c_tabulate(funcs,headers=["Command","Description"],cols=cols,title_cols=title)

    def load_args(function):
        cols = ['[E]',"[GR]",'[R]']
        inbt = ["","[E]:","[E]="]
        out = []
        for i,arg in enumerate(function.args):
            temp = ""
            for it,det in enumerate(arg):
                if det == None: break
                det = det if it<len(arg)-1 else repr(det)
                temp += f"{inbt[it]}{cols[it]}{det}"
            out.append(['','\n'][(i)%3==0 and i !=0 and len(function.args)>i] + temp)
        return "[E]" + '[G], '.join(out)

    def print_detailed_help(function):
        args = load_args(function)
            
        data = [[function.name,args,str(function.help or function.desc or '[BL]')]]
        cols = [["[L]"],["[E]"],["[P]"]]
        c_tabulate(data,headers=["Name","Args\n([E]name:[GR]type[E]=[R]default[B])","Description"],focus=["middle","middle","left"],cols=cols,title_cols=title)

    pre_loaded = [val for key,val in self.commands['pre'].items() if not key in ['description','long_description']]
    pre_loaded = self.commands['pre'].values()
    modules = [x for x in self.commands][1:]

    if not arg1 and not arg2:
        cprint(f"[Y]Functions\n")
        print_funcs(pre_loaded)

        cprint(f"\n[Y]Modules\n")
        funcs2 = [[x,self.commands[x]['description']] for x in modules]
        funcs = [[name,(desc or "")] for name,desc in funcs2]
        cols = [["[L]","[B]"],["[R]","[P]"]]
        c_tabulate(funcs,headers=["Name","Description"],cols=cols,title_cols=title)

    elif arg1 and not arg2:
        if not arg1 in self.commands and not arg1 in self.commands['pre']: 
            cprint(f"[R]Module not found")
            return 2
        if arg1 in self.commands:
            print_funcs([val for key,val in self.commands[arg1].items() if not key in ['description','long_description']],self.commands[arg1]['long_description'])
        else:
            print_detailed_help(self.commands['pre'][arg1])

    else:
        if not arg1 in self.commands or not arg2 in self.commands[arg1]:
            cprint(f"[R]Module or Function not found")
            return 2
        print_detailed_help(self.commands[arg1][arg2])
    print()        

def refresh(self):
    "Reloads all functions and commands"
    cdir = os.getcwd()
    os.chdir(sys.path[0])

    for x in self.modules:  
        sys.modules.pop(x)

    toload = ['base','custom']

    self.commands = {'pre':{}}
    self.modules = []
    self._load_functions(toload)
    
    for x in self.events:
        self.events[x] = []

    os.chdir(cdir)

def reload(self,module:str):
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

def load(self,module:str):
    "Import a module"
    dirs = ['base','commands']
    m = sys.path[0]
    print(m)

def cd(path:str):
    "Change current directory"
    if os.path.isdir(path):
        os.chdir(path)
    else:
        print("Directory not found. Does it exist?")
        return 2

def ls():
    "Directory listing"
    offset = 50
    raw = os.listdir()

    listing = {
        "file":[],
        "directory":[],
        "hidden_file":[],
        "hidden_directory":[]
    }

    for x in raw:
        offset = len(x)+6 if len(x) > offset else offset

        new = node(x)
        listing[new.type].append(new)

    def get_color(name):
        return [x for x in colors if x[:-1] in name and x.startswith(name[0])][0]

    def print_names(name1,name2):
        col1,col2 = get_color(name1),get_color(name2)
        names = [name1,name2] if len(listing[col1]) > len(listing[col2]) else [name2,name1]
        col1 = colors[get_color(names[0])]
        col2 = colors[get_color(names[1])]

        cprint(f"[G]__[ {col1}{names[0]}" + " "* (offset-len(names[0])+1) + f"[G]__[ {col2}{names[1]}" )
        cprint(f" [G]|" + ' '*(offset+3) + ' |')

    def output(ar1,ar2):
        array = [ar1,ar2] if len(ar1) > len(ar2) else [ar2,ar1]
        lar2 = len(array[1])

        for x in range(len(array[0])):
            ob1 = array[0][x]
            out = f" [G]|-[ {ob1.color}{ob1.name}"

            if x < lar2:
                ob2 = array[1][x]
                toff = offset - len(ob1.name)
                out += " "*toff + f" [G]|-[ {ob2.color}{ob2.name}"
            cprint(out)
        print()

    print_names("files","directories")
    output(listing['file'],listing['directory'])

    if any([len(x) > 0 for x in [listing['hidden_file'],listing['hidden_directory']]]):
        print_names("hidden_files","hidden_directories")
        output(listing['hidden_file'],listing['hidden_directory'])

def hide(*path:str, silent:bool=False):
    "Make file or folder hidden"
    __help__ = "[B]path [G]is the path to the file or folder from current directory"

    tohide = f"attrib +h {' '.join(path)}"
    if not os.path.isfile(' '.join(path)):
        cprint(f"[R]File not found")
        return 2

    os.system(tohide)
    if not silent:
        cprint(f'[GR]Succesfully hidden {" ".join(path)}')

def unhide(*path:str, silent:bool=False):
    "Unhide a hidden folder or file"
    __help__ = "[B]path [G]is the path to the file or folder from current directory"

    if not os.path.isfile(' '.join(path)):
        cprint(f"[R]File not found")
        return 2

    os.system(f"attrib -h {' '.join(path)}")
    if not silent:
        cprint(f"[GR]Succesfully unhid {' '.join(path)}")

def new(type:str,name:str,hidden:bool=False):
    "Makes a new empty folder or file"

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