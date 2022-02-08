from utils.cprint import *
from utils import shell
from utils import loader

from utils.highlight import *
from utils.suggestion import *
from utils.text import Text

from utils.utils import get_cursor, move_cursor, perserve_split

import msvcrt
import os
import sys

loader.load()

shell = shell.shell

suggestion = Suggestion(shell)
suggestion._update_data()

highlight = Highlight(shell)
highlight._update_data()

default = "[G]$dir$ [E]> [GR] "
data = shell.loader.load(default, _name="shell")


text = Text()
def new_input(prompt:str):
    print(prompt, end="")
    x,y = get_cursor()

    while 1:
        key = msvcrt.getch()

        if key == b'\x03': # CTRL + C
            raise KeyboardInterrupt

        elif key == b"\r": # Enter
            print()
            if text.text.strip() != '' and ( (text.history and text.history[0] != text.text) or (len(text.history)==0) ):
                text.history.insert(0, text.text)

            text.history_offset = -1
            return text.text

        elif key == b'\t': # Tab
            split = perserve_split(text.text, ' ')
            can_tab, suggest = suggestion.get(split.split_string)

            if suggest and can_tab:
                text.text = split.re_assemble(False).rstrip() + suggest

        else:
            text.do_action(key)
        
        # TEXT DISPLAY
        text.text = text.text.replace('\\', '\\\\')
        text.text = escape(text.text)

        split_text = perserve_split(text.text, ' ')
        
        if split_text:
            split_text.colors = highlight.apply(split_text.split_string)

        raw_colored = split_text.re_assemble()
        colored = cconvert(raw_colored).replace('\\\\', '\\')

        # Get suggestione
        split_text.reset(True)
        can_tab, suggest = suggestion.get(split_text.split_string) or ""
        suggest = raw_colored.rstrip() + '[G]' + suggest
        suggest = suggest.replace('\\\\', '\\')

        # Get arrow offset
        colored2 = colored
        if text.text_offset:
            split_text.string = text.text[:-text.text_offset]
            split_text._raw_split = split_text.split()
            split_text.reset(True)
            colored2 = cconvert(split_text.re_assemble()).replace('\\\\', '\\')

        move_cursor(x,y)
        print(f"{cconvert(suggest)}{' '*max(0, len(text.old_text)-len(decolor(suggest)))}", end="")

        move_cursor(x,y)
        print(colored2, end='')


        text.text = text.text.replace('\\\\', '\\')
        text.old_text = max([decolor(suggest), text.text], key=len)
        sys.stdout.flush()

if __name__ == "__main__":
    while 1:
        try:
            text.text = ''
            text.text_offset = 0
            cmd = new_input(cconvert(data.replace("$dir$",os.getcwd().replace("\\","/"))))
            if len(cmd)==0: continue
            shell.run(cmd.split())

        except KeyboardInterrupt:
            print()