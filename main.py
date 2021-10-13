from utils.shell import *
import os

shell = shell()

default = "[G]$dir$ [E]> [GR] "

data = shell.loader.load(default, _name="shell ")

while 1:
    try:
        cmd = input(cconvert(data.replace("$dir$",os.getcwd().replace("\\","/"))))
        if len(cmd)==0: continue
        shell.run(cmd.split())

    except KeyboardInterrupt:
        print()