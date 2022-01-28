import os,sys,json, re
import ctypes

from ctypes import wintypes

def is_int(string):
    try:
        return True,int(string)
    except:
        return False,None

def is_float(string):
    try:
        return True,float(string)
    except ValueError:
        return False,None

def is_bool(string):
    true = ['true','1','y','yes','on']
    false = ['false','0','n','no','off']
    if string.lower() in true+false: return True,string.lower() in true
    else: return False,None

def is_string(string):
    return True,string

types = {
    "int":is_int,
    "float":is_float,
    "bool":is_bool,
    "str":is_string
}

def is_windows():
    return os.name == 'nt'

def get_json(filename):
    path = sys.path[0] + f"/settings/{filename}"
    
    if os.path.isfile(path) and filename.endswith(".json"):
        with open(path) as f: return json.load(f)

def move_cursor(x:int, y:int) -> None:
    print(f"\x1b[{y};{x}H", end="")

def get_cursor():
    OldStdinMode = ctypes.wintypes.DWORD()
    OldStdoutMode = ctypes.wintypes.DWORD()
    kernel32 = ctypes.windll.kernel32
    kernel32.GetConsoleMode(kernel32.GetStdHandle(-10), ctypes.byref(OldStdinMode))
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), 0)
    kernel32.GetConsoleMode(kernel32.GetStdHandle(-11), ctypes.byref(OldStdoutMode))
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

    try:
        _ = ""
        sys.stdout.write("\x1b[6n")
        sys.stdout.flush()
        while not (_ := _ + sys.stdin.read(1)).endswith('R'):
            True
        res = re.match(r".*\[(?P<y>\d*);(?P<x>\d*)R", _)
        
    finally:
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), OldStdinMode)
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), OldStdoutMode)

    if(res):
        return (int(res.group("x")), int(res.group("y")))

    return (-1, -1)

class perserve_split():
    def __init__(self, string:str, char_split:str):
        self.string = string
        self.char_split = char_split

        self.colors = []
        self._raw_split = self.split()
        self.split_string = []
        
        self.reset()
    
    def __len__(self):
        return len(self.split_string)

    def reset(self, keep_colors:bool=False) -> None:
        self.split_string = [x for x in self._raw_split if not isinstance(x, int)]
        if not keep_colors:
            self.colors = ['']*len(self.split_string)

    def split(self) -> list:
        out = []

        char_temp = 0
        text_temp = ""
        for x in self.string:
            if x == self.char_split:
                if text_temp:
                    out.append(text_temp)
                    text_temp = ""

                char_temp += 1

            else:
                if char_temp:
                    out.append(char_temp)
                    char_temp = 0
                    
                text_temp += x

        if char_temp:
            out.append(char_temp)

        elif text_temp:
            out.append(text_temp)

        return out
    
    def re_assemble(self, apply_end:bool=True) -> str:
        output = list(self._raw_split)
        if not self._raw_split:
            return ''

        i = 0
        offset = 0 if isinstance(self._raw_split[0], str) else 1
        end_color = '[E]' if apply_end else ''

        for x in self._raw_split:
            if isinstance(x, int):
                i += 1
            else:
                output[max(0, i*2-offset)] = self.colors[i-offset] + self.split_string[i-offset] + end_color

        return ''.join(x if isinstance(x,str) else " "*x for x in output)