from sys import stdout as std
import traceback, importlib
import os,ast,sys
import utils.cprint as cpr
from utils.cprint import *
from utils.utils import *

class function():
    def __init__(self,func:callable,name:str,args:list,desc:str,help:str,module:str):
        self.times_run = 0

        self.func,self.name,self.args,self.desc,self.help,self.module = func,name,args,desc,help,module
        self.give_self = args[0][0] == "self" if len(args) >0 else False
        if self.give_self: self.args.pop(0)
    
    def run(self,args:list,kwargs:dict={}):
        self.times_run += 1
        return self.func(*args,**kwargs)

class shell():
    def __init__(self):
        self.root_path = sys.path[0].replace("\\","/")
        self.commands = {"pre":{}}
        self.modules = []
        self.events = {
            "on_load":[],
            "on_shell_ready":[],
            "on_ready":[]
        }
        self.running = []
        self.after_load = []
        self.cprint = cpr
        self._load_functions(['base','custom'])

    def run(self, command:str, help_if_error:bool=True):
        "Runs a function from module or runs as cmd"
        # Get function
        exit_code = 0
        print(cconvert('\r[G]'),end="")
        temp = self.get_function(command)
        if temp:
            func,targs = temp
            args = [[],{}]

            #Check if args match function args (type & amount)
            args[0] = self._check_args(targs[0],func)
            args[1] = self._check_args(targs[1],func)
            if not all([x!=False for x in args]): exit_code = 1

            # if function requests the shell class, give it as argument
            if func.give_self and exit_code == 0: 
                args[0].insert(0,self)

            #attempt running, with exceptions.
            self.running.append(func)
            if exit_code == 0:
                try: 
                    out = func.run(*args)
                    if out in [0,1,2]:
                        exit_code = out

                except SystemExit: exit()
                except: 
                    exit_code = 1
                    cprint(f"[R]{traceback.format_exc()}")


            self.running.pop()

        # If function not found, run as OS instead
        elif temp == None:
            exit_code = os.system(' '.join(command))

        else:
            exit_code = 1
        
        if exit_code == 1 and help_if_error and temp != None:
            path = self._get_function_path(command)
            self.run(f'help {path}'.split())

        return exit_code

    ## utility ##
    def _get_function_path(self,command:list):
        if command[0] in self.commands['pre']:
            return command[0]
        
        if command[0] in self.commands:
            if len(command) > 1 and command[1] in self.commands[command[0]]:
                return f"{command[0]} {command[1]}"

            elif 'main' in self.commands[command[0]]:
                return f"{command[0]} main"

            else:
                return command[0]

    def get_function(self,command:str):
        "get function and args from command"
        def get_args(args):
            kwargs = {}
            #loop through all args that start with '-' then invert the list to avoid incorrect index positioning
            for i,x in [[i+1,x] for i,x in enumerate(args) if x.startswith('-')][::-1]:
                #If '-' argument doesn't have a value, ignore it
                if len(args)<=i: continue

                kwargs[x[1:]] = args[i]
                args.pop(i)
            return ([x for x in args if not x.startswith('-')],kwargs)

        # If command pre-loaded give that 
        if command[0] in self.commands['pre']: return [self.commands['pre'][command[0]], get_args(command[1:])]

        if command[0] in self.commands:
            if len(command) > 1 and command[1] in self.commands[command[0]]:  
                # Get command and args
                return [self.commands[command[0]][command[1]], get_args(command[2:])]

            elif 'main' in self.commands[command[0]]: 
                # Get a module's main command if exists
                return [self.commands[command[0]]['main'], get_args(command[1:])]

            elif not len(command) > 1: 
                cprint("[R]Not enough arguments")
            else: 
                cprint("[R]Command not found")

            return False

    def _do_event(self,event:str):
        "Just do the event lol"
        try:
            for x in self.events[event]: x(self)
        except:
            cprint(f"[R]Error handling '{event}' event\n{traceback.format_exc()}")
        self.events[event] = []

    def _check_args(self,args,function:function):
        "Check if args are same type as function argument"
        new = []
        t_args = function.args
        if len(t_args) < len(args) and t_args[0][0][0] != "*":
            cprint(f"[R]Too many arguments for command")
            return False

        if type(args) == list:
            #Check all args give to see if they fit the given command variables
            # Eg: `def func(var1:int)` with command `func 389` it checks if '389' is a valid integer
            for i,x in enumerate(args):
                # Get default arg value
                argtype = t_args[i][1]
                if t_args[i][0].startswith("*"):
                    #Check if there's a type defined for this arg
                    if not argtype: 
                        for arg in args[i:]: new.append(arg)
                        continue
                    # Check if all given args are of defined type
                    for arg in args[i:]:
                        is_valid,output = types[argtype](arg)
                        if not is_valid:
                            cprint(f"[R]Argument '{t_args[i][0]}' should be of type {argtype}.")
                            return False
                        new.append(output)
                    return new
                is_valid,output = True, x
                if argtype:
                    is_valid,output = types[argtype](x) # Get string type (EG: if string matches int,float,bool etc.)
                
                if not is_valid: 
                    cprint(f"[R]Argument '{t_args[i][0]}' should be of type {argtype}.")
                    return False
                new.append(output)

        #Check kwargs
        elif type(args) == dict:
            new = {}
            # Loop through all kwargs
            for i,(k,v) in enumerate(args.items()):
                # Get default arg from function args
                in_arg = any([k in x for x in t_args])
                if not in_arg and not any(['**' in x[0] for x in t_args]):
                    cprint(f"[R]Unknown kwarg given: {k}")
                    return False
                #no clue what i did here, gl future me
                argtype = [x[1] for x in t_args if x[0] == k][0] if in_arg else [x[1] for x in t_args if x[0].startswith("**")][0]
                if not argtype: 
                    new[k] = v
                    continue #If none defined continue
                is_valid,output = types[argtype](v)

                if not is_valid: 
                    cprint(f"[R]Argument '{k}' should be of type {argtype}.")
                    return False
                new[k] = output

        return new

    def load_function(self,pyname:str,loc:str):
        "Load function into shell"
        # Get json to see which functions need to be pre-loaded (so you don't have to use `module function`)
        pre = get_json("pre_import.json") # type: ignore
        std.write(cconvert(f"\r[Y]Importing {pyname}...[E]"))
        std.flush()

        file = loc + pyname+'.py'
        pyfile = loc.replace("/",'.') + pyname

        #Import module
        try: 
            imlib = importlib.import_module(pyfile)
        except:
            std.write(cconvert(f"\r[R]Error importing {pyname}:\n\n{traceback.format_exc()}"))
            std.flush()
            return 1
        
        #Get module functions and description

        funcs = shell.get_functions(file)
        
        #Load data
        data = {}
        for f in funcs: 
            #Add to event list
            if f[0] in self.events:
                self.events[f[0]].append(getattr(imlib,f[0]))
                continue
            
            #Load into command storage
            data[f[0]] = function(getattr(imlib,f[0]),*f)
            self._do_event("on_load")
        key = pyname
        desc, long_desc = "",""

        if hasattr(imlib,"__desc__"):
            desc = getattr(imlib,"__desc__")
        if hasattr(imlib,"__long_desc__"):
            long_desc = getattr(imlib,"__long_desc__")

        #Check if module needs to be pre-loaded
        if pyname in pre: key = "pre"
        else: 
            data["description"] = desc
            data['long_description'] = long_desc

        #Load data into dict
        self.commands[key] = data
        self.modules.append(pyfile)
        std.write(cconvert(f"\r[GR]Succesfully imported the [G]{pyname}[GR] module[E]\n"))
        std.flush()

        self._do_event("on_ready")

    def _load_functions(self,dirs:list):
        "Load functions from directory"
        for x in dirs:
            loc = 'commands/'+x+'/'
            #Get all .py files in directory
            files = [x for x in os.listdir(loc) if x.endswith('.py')]
            
            for f in files:
                pyname = f.split('.')[0]
                self.load_function(pyname,loc)
        self._do_event("on_shell_ready")

    @staticmethod
    def get_functions(directory):
        "Get data from function"
        pyname = directory.split('/')[-1].split('.')[0]
        def top_level_functions(body):
            return (f for f in body if isinstance(f, ast.FunctionDef)) # Get all functions
        def parse_ast(filename): #Load AST for module
            with open(directory, "rt") as file:
                return ast.parse(file.read(), filename=filename)
        def get_desc(func_body): # Get the function description if exists
            for line in func_body:
                if isinstance(line,ast.Expr) and isinstance(line.value,ast.Constant): return line.value.value
        def get_help(func_body): # Get function __help__ value
            for line in func_body:
                if isinstance(line,ast.Assign) and isinstance(line.value,ast.Constant):
                    if line.targets[0].id == "__help__": return line.value.value
        def get_args(function): #Get function arguments with type indicator
            normal,varg,kwarg = [[arg.arg,(arg.annotation.id if arg.annotation else None),get_default(function.args.defaults,arg)] for arg in function.args.args],function.args.vararg,function.args.kwarg
            if varg:normal.append(["*"+varg.arg,(varg.annotation.id if varg.annotation else None),None])
            if kwarg: normal.append(['**'+kwarg.arg,(kwarg.annotation.id if kwarg.annotation else None),None])
            return normal
        def get_default(defaults,arg): #Get default value from args
            for default in defaults:
                if default.col_offset == arg.end_col_offset+1: return default.value

        parsed = parse_ast(directory)
        funcs = top_level_functions(parsed.body)

        #Make and return list of it all
        return [[f.name,get_args(f),get_desc(f.body),get_help(f.body),pyname] for f in funcs if not f.name.startswith("_")]