import time
from utils.cprint import *
from utils.shell import command
__long_desc__ = """[R]Timeit[P]

A module used to time how long a command takes to execute."""
__desc__ = "Time how long it takes to run a certain command"

@command("Time how long it takes to run a command")
def main(self,*command:str):
    "Time how long it takes to run a command"
    __help__ = "[B]Command[G] is a shell command"

    cprint(f"[P]Timing command '[Y]{' '.join(command)}[P]'\n{'-'*30}\n")
    start = time.time()

    self.run(command, help_if_error=False)

    end = time.time()
    total = end - start
    cprint(f"[P]\n{'-'*30}\n[P]Command finished in [Y]{total:.4f}[P] seconds")