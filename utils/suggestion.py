import os
from utils.shell import function

class Suggestion():
    def __init__(self, shell):
        self.shell = shell
        self.modules = []
    
    def _get_functions(self, module:str):
        return {k:v for k,v in self.shell.commands[module].items() if isinstance(v, function)}


    def _update_data(self):
        self.modules = list(self.shell.commands)


    def _get_args(self, module:str, function:str, args:list):
        filename =  module

        if hasattr(self.shell.raw_import[filename], f"_{function}_suggestion"):
            custom_sugg = getattr(self.shell.raw_import[filename], f"_{function}_suggestion")(self.shell, args)

            if type(custom_sugg) in (list, tuple) and len(custom_sugg) == 2 and isinstance(custom_sugg[0], bool) and isinstance(custom_sugg[1], str):
                return custom_sugg

        f_args = self.shell.commands[module][function].args
        out = [f"{'!' if x[2] == 'None' else ''}{x[0]}" for x in f_args[len(args):]]
        return False, ' '+', '.join(out)


    def _get_sub(self, module:str, args:list):
        funcs = self._get_functions(module)

        if 'main' in funcs:
            return self._get_args(module, 'main', args)
        
        elif len(args) <= 1:
            arg = args[0] if len(args) else ''
            space = '' if arg else ' '

            closest = [x for x in funcs if x.startswith(arg)]
            
            if closest:
                return True, f"{space}{closest[0][len(arg):]}"

    
    def _get_suggestion(self, command:list):
        cmd = command[0]
        if len(command) == 1 and not cmd in self.modules:
            commands = [x for x in self.modules if x.startswith(cmd)]
            file = [x for x in os.listdir() if os.path.isfile(x) and x.startswith(cmd)]
            
            if commands:
                return True, commands[0][len(cmd):]

            elif file:
                return True, file[0][len(cmd):]
            
        elif len(command) >= 1:
            sub = command[1] if command[1:] else ""

            if cmd in self.modules and not sub in self._get_functions(cmd):
                return self._get_sub(cmd, command[1:])
            
            elif cmd in self.modules and sub in self._get_functions(cmd):
                return self._get_args(cmd, sub, command[2:])


    def get(self, command:list):
        if not command:
            return False,""

        suggestion = self._get_suggestion(command)
        return suggestion or [False, ""]