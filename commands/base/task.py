import os, json, subprocess
from utils.cprint import *
from utils.shell import command

__long_desc__ = """[R]Task[P]

Task is a easy way to kill multiple processes within the commandline.
It's used mainly to kill programs that have multiple processes keeping it alive."""
__desc__ = "Kill multiple processes with one command"

@command("Kills multiple processes at once")
def kill(*processes:str):
    "Kills multiple processes"
    __help__ = "[B]processes [G]are process [B]names[G] or [B]PID's[G] devided by [B],"

    processes = [x.strip() for x in ' '.join(processes).split('&')]

    data = os.popen(f"tasklist /FO csv /V").read().replace('\\','\\\\').splitlines()
    found = []

    for x in data:
        name,pid,_,_,memory,status,executor,time,title = json.loads(f"[{x}]", strict=False)
        if any(any(y.lower() in str(z).lower() for z in [name, pid, title]) for y in processes):
            found.append([name,pid,memory,status,executor,time,title])
    
    titles = "Name,Pid,Memory,Status,Executor,Cpu Time,Title".split(',')
    cols = "[L],[B],[Y],[G],[G],[B],[G]".split(',')
    c_tabulate(found, titles, cols=cols, title_cols=cols)
    
    print('')
    if not found:
        return

    do = input(cconvert(f"[R]Do you want to kill these processes? [G](Y/N): [Y]"))
    while do.lower() not in ['y','n']:
        print(f"Please input either 'y' or 'n'")
        do = input(cconvert(f"[R]Do you want to kill these processes? [G](Y/N): [Y]"))
    
    if do.lower() != 'y':
        return

    print()
    for x in found:
        pid = x[1]
        popen = subprocess.Popen(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out,err = popen.communicate()

        if out:
            cprint(f"[GR]Succesfully killed [E]{pid}")
        else:
            if "not found" in err.decode():
                cprint(f"[Y]Process already killed [E]{pid}")
            else:
                cprint(f'[R]Unable to kill process [E]{pid}')