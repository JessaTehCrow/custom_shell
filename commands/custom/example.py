from utils.shell import command, event
# Define description of the module
__desc__ = "Some example module"

__long_desc__ = """[R]example[P]

Some description here"""

# All event(s)
@event("on_load")
def on_load(_):
    "This will be run when this function has loaded"

    print(f"\rExample: Function loaded!")

@event("on_ready")
def on_ready(_):
    "This will run when the module has been loaded"

    print("Example: Module Loaded")

@event("on_shell_ready")
def on_shell_ready(_):
    "This will be run when everything has finished importing / loading"

    print("Example: Shell ready")

# Local function(s)
def _local_function(integer:int):
    "This is a local function, and will not be visible to the end-user"

    return integer ** 2

# Function run when either `example [args]` or `example main [args]`
@command("This will run if you provide no sub-function",
"""[L]A more detailed description for this function!
[B]Variable[G] Any string value
Prints the given string""")
def main(variable:str="Some default value"):
    print(variable)

# Function only run when `example test [args]`
@command("Some example function",
"""[L]A more detailed description for this function!
[B]Variable[G] Any non-decimal number
Prints the value of [B]X [G]squared
""")
def test(variable:int=3):
    print( _local_function( variable ) )

# Function that gets the shell object
@command("Getting the shell object",
"""[G]No arguemnts for this function""")
def test2(self):
    # Use "self.cprint" to use the cprint module without needing to import it
    self.cprint.cprint("[B]Currently running command:[P]",self.running[-1].name)