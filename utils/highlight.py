from utils.cprint import cconvert, escape
from utils.shell import function
from utils.utils import types

import os

colors = {
    "text_color":'[E]',
    "command" : "[B]",
    "sub_command" : "[GR]",

    "bool_arg" : "[B]",
    "int_arg" : "[L]",
    "float_arg" : "[L]",
    "str_arg" : "[Y]",

    "wrong_arg" : "[R][U][BO]",
    "file_color" : "[GR]"
}

class Highlight():
    def __init__(self, shell):
        self.shell = shell
        self.modules = []
        self.commands = []
        self.colors = shell.loader.load(colors, "colors", "shell")
    
    def _get_functions(self, module:str):
        return {k:v for k,v in self.shell.commands[module].items() if isinstance(v, function)}


    def _update_data(self):
        self.modules = list(self.shell.commands)[1:]
        self.commands = self.modules + list(self.shell.commands['pre'])


    def _get_args(self, module:str, function:str, args:list):
        cols = [None]*len(args)

        file = "commands" if module == 'pre' else module
        if not module in self.shell.commands or not function in self.shell.commands[module]:
            return

        if hasattr(self.shell.raw_import[file], f"_{function}_highlight"):
            return getattr(self.shell.raw_import[file], f"_{function}_highlight")(self.shell, args)

        f_args:list = self.shell.commands[module][function].args

        for i, f_arg in enumerate(f_args):
            if i >= len(args):
                break

            arg_type = f_arg[1]
            color = self.colors['text_color']

            if arg_type and arg_type+"_arg" in self.colors:
                correct, _ = types[arg_type](args[i])

                color = self.colors[arg_type+"_arg"]
                if not correct:
                    color = self.colors['wrong_arg']

            cols[i] = color
        
        for i, arg in enumerate( args[len(f_args):] ):
            color = self.colors['wrong_arg']
            
            if len(f_args) and f_args[-1][0].startswith("*"):
                l_arg = f_args[-1]
                if not l_arg[1]:
                    color = self.colors['text_color']
                else:
                    correct, _ = types[l_arg[1]](args[i+len(f_args)])
                    
                    if correct:
                        color = self.colors[l_arg[1]+"_arg"]
            
            cols[i+len(f_args)] = color
        
        return cols


    def _get_highlight(self, command:list):
        command_copy = list(command)
        cols = [self.colors["text_color"]]*len(command)
        
        module = command_copy[0]
        func = None

        # main command
        if command[0] in self.commands:
            cols[0] = self.colors["command"]

        # If command[0] can't be found, check if it's a file in the current directory

        elif command[0] in [x for x in os.listdir() if os.path.isfile(x)]:
            cols[0] = self.colors["file_color"]
            return cols

        # sub-command
        if len(command) > 1 and command_copy[0] in self.modules and command[1] in self._get_functions(command_copy[0]):
            func = command_copy[1]
            cols[1] = self.colors["sub_command"]
        
        # get args
        args_offset = 1
        if not command_copy[0] in self.modules:
            func = str(module)
            module = "pre"

        elif len(command) > 1 and (module in self.modules) and ('main' in self._get_functions(module)) and (func not in self._get_functions(module)):
            func = "main"

        else:
            args_offset = 2
        
        args = command[args_offset:]
        args = self._get_args(module, func, args)

        if args:
            cols[args_offset:] = args
        
        return cols
        
    def apply(self, command:list):
        colors = self._get_highlight(command)
        colors = colors
        return colors