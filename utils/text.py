import string
import msvcrt
from utils.utils import perserve_split

class Text():
    def __init__(self):
        self.chars = string.printable[:-5].encode()
        self.old_text = ""
        self.text = ""
        self.text_offset = 0

        self.history_offset = 0
        self.history = []

        self.actions = {
            b"\x08" : self._backspace,
            b"\x7f" : self._ctrl_backspace,
            b"\xe0" : self._other,
            b"\x1b" : self._escape,
            b"\x00" : self._function
        }

    def do_action(self, action):
        if action in self.chars:
            self._char(action)
            return

        if not action in self.actions:
            return
        
        return self.actions[action](action)
    
    #### CLASS FUNCS ####
    def __repr__(self):
        return self.text
    
    
    def __len__(self):
        return len(self.text)


    #### ACTIONS ####
    def _char(self, char:bytes):
        offset = len(self.text) - self.text_offset
        self.text = self.text[:offset] + char.decode() + self.text[offset:]


    def _backspace(self, _):
        offset = len(self.text) - self.text_offset
        self.text = self.text[:max(0,offset-1)] + self.text[offset:]


    def _get_perserve_index(self):
        raw = perserve_split(self.text, ' ')
        if not raw.split_string:
            return None, None

        offset = len(self.text) - self.text_offset

        raw_offset = int(offset)
        left = 0

        for index, v in enumerate(raw._raw_split):
            left = int(raw_offset)

            if isinstance(v, int):
                raw_offset -= v
            else:
                raw_offset -= len(v)

            if raw_offset <= 0:
                break
        return index, left


    def _ctrl_backspace(self, _):
        index, left = self._get_perserve_index()
        if [index,left] == [None, None]:
            return
            
        raw = perserve_split(self.text, ' ')

        if isinstance(raw._raw_split[index], int):
            raw._raw_split[index] -= left
        else:
            raw._raw_split[index] = raw._raw_split[index][left:]
        
        raw.reset()
        self.text = raw.re_assemble(False)


    def _arrow(self, key:bytes):
        key = key.decode()
        left, up, right, down = "K H M P".split()

        if key in (up, down) and self.history:
            self.history_offset += [-1,1][key==up]
            self.history_offset = max(-1, min(self.history_offset, len(self.history)-1))

            if self.history_offset == -1:
                self.text = ""
            else:
                self.text = self.history[self.history_offset]
        
        if key in (left, right):
            self.text_offset += [1,-1][key==right]
            self.text_offset = max(0, min(len(self.text), self.text_offset))
    
    def _ctrl_arrow(self, key:bytes):
        left, up, right, down = b"s \x8d t \x91".split(b" ")


    def _delete(self):
        offset = len(self.text) - self.text_offset
        prev = len(self.text)
        self.text = self.text[:offset] + self.text[offset+1:]

        if len(self.text) != prev:
            self.text_offset -= 1

    def _other(self, _):
        arrows = b"KHMP"
        ctrl_arrow = b"st\x91\x8d"
        other_actions = {
            b"S" : self._delete,
            b"s" : self._ctrl_arrow
        }
        
        key = msvcrt.getch()
        if key in arrows:
            self._arrow(key)

        elif key in ctrl_arrow:
            self._ctrl_arrow(key)

        elif key in other_actions:
            other_actions[key]()

        else:
            self.text = key

    def _escape(self, _):
        self.history_offset = -1
        self.text_offset = 0
        self.text = ""


    #We want to ignore function keys... for now
    def _function(self, _):
        ignored_key = msvcrt.getch()