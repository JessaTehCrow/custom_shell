# Define description of the module
__desc__ = "Some example module"

__long_desc__ = """[R]example[P]

Some description here"""

# All event(s)
def on_load(_):
    "This will be run when this function has loaded"

    print(f"\rExample: Function loaded!")

def on_ready(_):
    "This will run when the module has been loaded"

    print("Example: Module Loaded")

def on_shell_ready(_):
    "This will be run when everything has finished importing / loading"

    print("Example: Shell ready")

# Local function(s)
def _local_function(integer:int):
    "This is a local function, and will not be visible to the end-user"

    return integer ** 2

# Function run when either `example [args]` or `example main [args]`
def main(variable:str="Some default value"):
    "This will run if you provide no function"

    __help__ = "[L]A more detailed description for this function!\n[B]Variable[G] Any string value\nPrints the given string"

    print(variable)

# Function only run when `example test [args]`
def test(variable:int=3):
    "Some example function"

    __help__ = "[L]A more detailed description for this function!\n[B]Variable[G] Any non-decimal number\nPrints the value of [B]X [G]squared"

    print( _local_function( variable ) )