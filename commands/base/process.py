import subprocess,time,math,sys
from subprocess import PIPE,STDOUT
from utils.cprint import c_tabulate, cprint

from utils.shell import command, event

__long_desc__ = """[R]Process[P]

Process is a module that helps you run shell commands in the background
Making it easier to do multiple things at the same time, without having to open another console window"""
__desc__ = "Run a command in the background"
handler = None

class _handler():
    def __init__(self,shell,bdir):
        self.shell = shell
        self._batdir_ = bdir
        self.processes = []
    
    def new_process(self,command):
        try:
            process = subprocess.Popen(f"{self._batdir_} & "+' '.join([x for x in command])+f" & {self._batdir_}", shell=True,stdin=PIPE, stdout=PIPE, stderr=STDOUT)
            process.start = time.time()
            self.processes.append([' '.join(command),process])

            cprint(f"[GR]Succesfully started process with pid [B]{process.pid}")
        except Exception as e:
            cprint(f"[R]Unable to start process: [Y]{e}")
    
    def check(self):
        def local_time(num):
            return time.strftime("%I:%M:%S %p",time.localtime(num))
        def get_time(process):
            to_number = lambda string: sum([int(v1*v2) for v1,v2 in zip([float(x) for x in string.split(':')],[360000,6000,100])])
            starttime = local_time(process.start)
            if process.poll() == None:
                return [starttime,f"{time.time() - process.start:.2f} Seconds","N/A"]

            if process.returncode == 0:
                data = [x.replace('\r','') for x in process.communicate()[0].decode().split('\n')]
                etime = to_number(data[-2])
                eltime = (etime - to_number(data[0])) / 100
                return [starttime,f"{eltime:.2f} Seconds",local_time(process.start + eltime)]
            else:
                return [starttime,'N/A',"Killed"]

        toprint = [[str(i+1),repr(command),["[GR]Finished","[Y]Running"][process.poll()==None],*get_time(process),str(process.pid)] for i,(command,process) in enumerate(self.processes)]
        
        cols = [["[G]","[E]"],["[P]","[R]"],"[E]","[G]",'[G]','[G]','[L]']
        titles = ['ID','Command',"Status","Start","Elapsed","Finished","PID"]
        title_cols = "[B]"
        focus = ['middle','left','left','middle','middle','middle','left']
        print()
        c_tabulate(toprint,titles,cols=cols,title_cols=title_cols,focus=focus,sort="Status")
        print()
    
    def output(self,ID):
        if len(self.processes)<ID:
            cprint(f"[R] ID doesn't exist. 1-{len(self.processes)}")
            return
        command,process = self.processes[ID-1]
        running = process.poll()==None

        if running: 
            cprint(f"[R] Process still running, unable to access output.")
            return
        if process.returncode != 0:
            cprint(f"[R] Process not properly closed, unable to access output")
            return
        output = '\n'.join(process.communicate()[0].decode().split('\n')[1:-2])
        cprint(f"\n[Y]Showing output for '[G]{process.pid}[Y]' with command '[G]{command}[Y]':[E]\n{'-'*50}")
        cprint(output)
        cprint("\n"+"-"*50)

@event("on_ready")
def on_ready(self):
    global handler
    _batdir_ = self.root_path + "/commands/custom/ptime"
    handler = _handler(self,_batdir_)
    handler.processes = self._background.processes if hasattr(self,"_background") else []
    self._background = handler
    print("Handler succesfully initialized")

@command("Runs a non shell command as background process", "[B]Command[G] Any cmd command")
def run(*command:str,**other:str):
    command = list(command)
    for k,v in other.items(): command += [f'-{k}',v]

    handler.new_process(command)

@command("Clears all finished processes")
def clear():
    "Clears all finished processes"
    to_remove = []
    for cmd,process in handler.processes:
        if process.poll() == None: continue
        to_remove.append([cmd,process])

    for cmd,process in to_remove:
        handler.processes.remove([cmd,process])
        cprint(f"[GR]Removed process with PID '[B]{process.pid}[GR]' with command '[G]{cmd}[GR]'")

@command("Shows output for finished process", "[B]ID[G] is the ID of the process.\n[G](Can be found using 'process data')")
def output(ID:int):
    handler.output(ID)

@command("Shows which processes are running")
def data():
    handler.check()