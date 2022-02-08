import traceback, inspect
import os, sys

import utils.cprint as cpr
import types as Types

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

class Shell():
    def __init__(self):
        self.root_path = sys.path[0].replace("\\","/")
        self.commands = {}
        self.raw_import = {}
        self.modules = []
        self.events = {
            "on_load":[],
            "on_shell_ready":[],
            "on_ready":[]
        }
        self.running = []
        self.after_load = []
        self.cprint = cpr

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

            if any((x == None) for x in args[0]) or any((x == None) for x in args[1]):
                cprint(f"\n[R]Invalid argument type given\n")
                exit_code = 1

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
        if command[0] in self.commands:
            if len(command) > 1 and command[1] in self.commands[command[0]]:
                return f"{command[0]} {command[1]}"

            elif 'main' in self.commands[command[0]]:
                return f"{command[0]} main"

            else:
                return command[0]


    def load_kwargs(self,args:list):
        kwargs = {}
        #loop through all args that start with '-'
        for i,x in [[i+1,x] for i,x in enumerate(args) if x.startswith('-')]:
            #If '-' argument doesn't have a value, ignore it
            if len(args)<=i: continue

            kwargs[x[1:]] = args[i]
            args.pop(i)
        return kwargs


    def get_args(self,args:list,func):
        kwargs = {}

        kwargs = self.load_kwargs(args)
        return ([x for x in args if not x.startswith('-')],kwargs)


    def get_function(self,command:list):
        "get function and args from command"

        if command[0] in self.commands:
            if len(command) > 1 and command[1] in self.commands[command[0]]:  
                # Get command and args
                func = self.commands[command[0]][command[1]]
                return [func, self.get_args(command[2:],func)]

            elif 'main' in self.commands[command[0]]: 
                # Get a module's main command if exists
                func = self.commands[command[0]]['main']
                return [func, self.get_args(command[1:],func)]

            elif not len(command) > 1: 
                cprint("[R]Not enough arguments")
            else: 
                cprint("[R]Command not found")

            return False


    def _do_event(self,event:str):
        "Just do the event lol"
        try:
            for x in self.events[event]: 
                self.running.append(x)
                x(self)
                self.running.pop()
        except:
            cprint(f"[R]Error handling '{event}' event\n{traceback.format_exc()}")
        self.events[event] = []


    def _check_args(self,args,function:function):
        "Check if args are same type as function argument"
        new = []
        t_args = function.args
        if len(t_args) < len(args) and not any([x[0][0] == '*' for x in t_args]):
            cprint(f"[R]Too many arguments for command")
            return [None]

        if len(t_args) > 0 and (any([x[0][0] == '*' for x in t_args]) and type(args) == list):
            if t_args[0][1] == None:
                return args

            for x in args:
                valid, out = types[t_args[0][1]](x)
                if not valid:
                    new.append(None)
                else:
                    new.append(out)

            return new

        if type(args) == list:
            #Check all args give to see if they fit the given command variables
            # Eg: `def func(var1:int)` with command `func 389` it checks if '389' is a valid integer
            for i,x in enumerate(args):

                # Get default arg value
                argtype = t_args[i][1]
                if t_args[i][0].startswith("*"):
                    #Check if there's a type defined for this arg

                    if argtype == '_empty': 
                        for arg in args[i:]: new.append(arg)
                        continue

                    # Check if all given args are of defined type
                    for arg in args[i:]:
                        is_valid,output = types[argtype](arg)
                        if not is_valid:
                            cprint(f"[R]Argument '{t_args[i][0]}' should be of type {argtype}.")
                            return [None]
                        new.append(output)

                    return new

                is_valid,output = True, x
                if argtype != '_empty':
                    is_valid,output = types[argtype](x) # Get string type (EG: if string matches int,float,bool etc.)
                
                if not is_valid: 
                    cprint(f"[R]Argument '{t_args[i][0]}' should be of type {argtype}.")
                    return [None]
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
                    return None
                    
                #no clue what i did here, gl future me
                argtype = next(x[1] for x in args if (in_arg and x[0] == k) or x[0].startswith("**"))

                if argtype == '_empty': 
                    new[k] = v
                    continue #If none defined continue

                is_valid,output = types[argtype](v)

                if not is_valid: 
                    cprint(f"[R]Argument '{k}' should be of type {argtype}.")
                    return None
                new[k] = output

        return new


shell = Shell()


def _get_module(stack):
    frame = stack[1]
    module = inspect.getmodule(frame[0])
    filename = module.__file__

    return filename.split('\\')[-1][:-3]


def _to_function(func, module, desc="", help=""):
    signature = inspect.signature(func)

    args = []
    for k, v in signature.parameters.items():
        name = str(v).split(':')[0].split('=')[0]
        args.append([name, v.annotation.__name__, v.default])

    return function(func, func.__name__, args, desc, help, module)



def command(description='', help=''):
    module = _get_module(inspect.stack())

    def inner(func):
        shell.commands[module][func.__name__] = _to_function(func, module, description, help)
        return func

    if isinstance(description, Types.FunctionType):
        func = description

        shell.commands[module][func.__name__] = _to_function(func, module, help)
        return func

    shell._do_event('on_load')
    return inner


def event(event_name:str):
    def inner(func):
        if not event_name in shell.events:
            cprint(f"[R]Event {event_name} is not a valid event.")
            return func

        shell.events[event_name].append(func)
        return func

    return inner