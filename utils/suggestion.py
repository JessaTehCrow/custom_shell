import os
from utils.shell import function

class Suggestion():
    def __init__(self, shell):
        self.shell = shell
        self.modules = []
    
    # get all functions from modules
    def _get_functions(self, module:str):
        return {k:v for k,v in self.shell.commands[module].items() if isinstance(v, function)}

    # Get all modules
    def _update_data(self):
        self.modules = list(self.shell.commands)

    # Get suggestions for functions
    def _get_args(self, module:str, function:str, args:list):
        filename =  module

        # If there's a custom suggestion function available, use that
        if hasattr(self.shell.raw_import[filename], f"_{function}_suggestion"):
            custom_sugg = getattr(self.shell.raw_import[filename], f"_{function}_suggestion")(self.shell, args)

            if type(custom_sugg) in (list, tuple) and len(custom_sugg) == 2 and isinstance(custom_sugg[0], bool) and isinstance(custom_sugg[1], str):
                return custom_sugg

        f_args = self.shell.commands[module][function].args

        # Get names for arguments and show if optional or not
        out = [f"{'!' if x[2] == 'None' else ''}{x[0]}" for x in f_args[len(args):]]
        
        # join it all together (but don't allow tab complete)
        return False, ' '+', '.join(out)

    # Get sub-function suggestions
    def _get_sub(self, module:str, args:list):
        funcs = self._get_functions(module)

        if 'main' in funcs:
            return self._get_args(module, 'main', args)
        
        elif len(args) <= 1:
            # get args
            arg = args[0] if len(args) else ''

            # Don't know how to explain this- but blah blah, empty spot unless already typed
            space = '' if arg else ' '
            
            # Get anything you can suggest into
            closest = [x for x in funcs if x.startswith(arg)]
            
            # IF there's anything that you *CAN* autocomplete into, suggest that
            if closest:
                return True, f"{space}{closest[0][len(arg):]}"

    
    def _get_suggestion(self, command:list):
        cmd = command[0]
        
        # if command is not a module
        if len(command) == 1 and not cmd in self.modules:
            # Get all modules that start with the current cmd input
            commands = [x for x in self.modules if x.startswith(cmd)]
            
            # Get all files in current directory that start with the current cmd input
            file = [x for x in os.listdir() if os.path.isfile(x) and x.startswith(cmd)]
            
            # If there's a command you could complete into, suggest that over files, and allow it to be tab-completed
            if commands:
                return True, commands[0][len(cmd):]

            # If there's no possible command, suggest a file (if it exists) and allow it to be tab-completed
            elif file:
                return True, file[0][len(cmd):]
        
        # If there's more than 1 argument (or cmd matched a module)
        elif len(command) >= 1:
            # Get sub command
            sub = command[1] if command[1:] else ""

            # If cmd is a module, and the second cmd entry is not a valid sub-function, parse sub function
            if cmd in self.modules and not sub in self._get_functions(cmd):
                return self._get_sub(cmd, command[1:])
            
            # If cmd is a module, and the second cmd entry is a sub function, parse arguments
            elif cmd in self.modules and sub in self._get_functions(cmd):
                return self._get_args(cmd, sub, command[2:])

    def get(self, command:list):
        if not command:
            return False,""

        suggestion = self._get_suggestion(command)
        return suggestion or [False, ""]