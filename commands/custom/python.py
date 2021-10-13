from cprint import *
__long_desc__ = """[R]python[P]

A module used to run some python code without having to make a script, or open the python intepeter"""
__desc__ = "Run python from the commandline"

def main(*command:str):
    "Run python from commandline"
    __help__ = "[B]command [G]Python code as a single line"
    command = ' '.join(command)
    exec(command)