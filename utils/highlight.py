from utils.shell import function
from utils.utils import types

import os

# Default color scheme
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
        
        # Load custom color scheme
        self.colors = shell.loader.load(colors, "colors", "shell")
    
    def _get_functions(self, module:str):
        # Load all functions of modules from shell
        return {k:v for k,v in self.shell.commands[module].items() if isinstance(v, function)}

    # Get all modules from shell
    def _update_data(self):
        self.modules = list(self.shell.commands)

    # Here's where the fun 'idk what the fuck this' is happens
    def _get_args(self, module:str, function:str, args:list):
        # Prepare a list as long as the arguments
        cols = [None]*len(args)

        file = module

        # if the command doesn't exist, ignore this pass
        if not module in self.shell.commands or not function in self.shell.commands[module]:
            return
        
        # If a custom highlighting function is available, use that
        if hasattr(self.shell.raw_import[file], f"_{function}_highlight"):
            return getattr(self.shell.raw_import[file], f"_{function}_highlight")(self.shell, args)

        # get function args
        f_args:list = self.shell.commands[module][function].args

        # Loop through function args
        for i, f_arg in enumerate(f_args):
            if i >= len(args): # If more function args than passed args, continue to next
                break
            
            # Get argument type (int, str, etc.)
            arg_type = f_arg[1]
            color = self.colors['text_color']

            # get the color for the argument
            if arg_type and arg_type+"_arg" in self.colors:
                correct, _ = types[arg_type](args[i])

                color = self.colors[arg_type+"_arg"]
                if not correct:
                    color = self.colors['wrong_arg']
            
            # Set the color
            cols[i] = color
        
        # Loop through 
        for i, arg in enumerate( args[len(f_args):] ):
            color = self.colors['wrong_arg'] # default color
            
            # If it's an starred argument, 
            if len(f_args) and f_args[-1][0].startswith("*"):
                l_arg = f_args[-1]

                # If the function argument does not have any associated datatype, make the color text color
                if l_arg[1] == '_empty':
                    color = self.colors['text_color']

                else:
                    # Very cryptic, but all it does is see if the user argument is the same datatype as the function argument
                    correct, _ = types[l_arg[1]] (args[i+len(f_args)])
                    
                    if correct:
                        color = self.colors[l_arg[1]+"_arg"]
                        # Get color for thing
            
            # Set color
            cols[i+len(f_args)] = color
        
        # Return colors
        return cols

    # More cryptic fun
    def _get_highlight(self, command:list):
        # copy command
        command_copy = list(command)

        # Prepare color array
        cols = [self.colors["text_color"]]*len(command)
        
        # default values
        args_offset = 2
        module = command_copy[0]
        func = None

        # main command
        if command[0] in self.modules:
            cols[0] = self.colors["command"]

        # If command[0] can't be found, check if it's a file in the current directory
        if command[0] in [x for x in os.listdir() if os.path.isfile(x)]:
            cols[0] = self.colors["file_color"]
            return cols

        # if there's at least 2 items in the split command, and the second entry is a sub-function for the module
        if len(command) > 1 and command_copy[0] in self.modules and command[1] in self._get_functions(command_copy[0]):
            func = command_copy[1]
            cols[1] = self.colors["sub_command"]
        
        # if there's at least 2 items in the split command, and `main` in the module and the second entry in the split command is not a sub-function, parse it as arguments for main
        if len(command) > 1 and (module in self.modules) and ('main' in self._get_functions(module)) and (func not in self._get_functions(module)):
            func = "main"
            args_offset = 1 
        
        # Get argument highlight
        args = command[args_offset:]
        args = self._get_args(module, func, args)

        if args:
            cols[args_offset:] = args
        
        # Return colors
        return cols
        
    def apply(self, command:list):
        colors = self._get_highlight(command)
        colors = colors
        return colors