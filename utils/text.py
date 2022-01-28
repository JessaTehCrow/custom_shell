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


    def _ctrl_backspace(self, _):
        raw = perserve_split(self.text, ' ')
        is_int = isinstance(raw._raw_split[-1], int) and raw._raw_split[-1] == 1
        raw._raw_split = raw._raw_split[:-(1+is_int)]
        raw.reset() 

        self.text = raw.re_assemble(False)
        if self.text == " ":
            self.text = ""


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


    def _delete(self):
        offset = len(self.text) - self.text_offset
        prev = len(self.text)
        self.text = self.text[:offset] + self.text[offset+1:]

        if len(self.text) != prev:
            self.text_offset -= 1

    def _other(self, _):
        arrows = b"KHMP"
        other_actions = {
            b"S" : self._delete
        }
        
        key = msvcrt.getch()
        if key in arrows:
            self._arrow(key)
        
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