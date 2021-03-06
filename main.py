from utils.cprint import *
from utils import shell as Shell
from utils import loader

from utils.highlight import *
from utils.suggestion import *
from utils.text import Text

from utils.utils import get_cursor, move_cursor, perserve_split

import traceback
import msvcrt
import os
import sys
import time


text = Text()
def new_input(prompt:str, highlight, suggestion, text:Text, _old=""):
    print(prompt, end="")
    x,y = get_cursor()

    while 1:
        key = msvcrt.getch()

        if key == b'\x03': # CTRL + C
            raise KeyboardInterrupt

        elif key == b"\r": # Enter
            print()
            if text.text[-2:] in [' ^']: # `\` will be added later
                out = text.text[:-1] + new_input(cconvert("[G]: "), highlight, suggestion, Text(), _old+text.text[:-1])
                text.history.insert(0, out)
                return out

            if text.text.strip() != '' and ( (text.history and text.history[0] != text.text) or (len(text.history)==0) ):
                text.history.insert(0, text.text)

            text.history_offset = -1
                
            return text.text

        elif key == b'\t': # Tab
            split = perserve_split(_old+text.text, ' ')
            can_tab, suggest = suggestion.get(split.split_string)

            if suggest and can_tab:
                text.text = split.re_assemble(False, len(perserve_split(_old, ' ')._raw_split)).rstrip() + suggest

        else:
            text.do_action(key)
        
        # TEXT DISPLAY
        text.text = text.text.replace('\\', '\\\\')
        text.text = escape(text.text)

        split_text = perserve_split(_old + text.text, ' ')
        
        if split_text:
            split_text.colors = highlight.apply(split_text.split_string)

        raw_colored = split_text.re_assemble(assemble_offset=len(perserve_split(_old, ' ')._raw_split))
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

def main():
    loader.load()

    shell = Shell.shell

    suggestion = Suggestion(shell)
    suggestion._update_data()

    highlight = Highlight(shell)
    highlight._update_data()

    default = "[G]$dir$ [E]> [GR] "
    data = shell.loader.load(default, _name="shell")

    shell._suggestion = suggestion
    shell._highlight = highlight

    run = 0
    while 1:
        try:
            text.text = ''
            text.text_offset = 0

            cmd = new_input(cconvert(data.replace("$dir$",os.getcwd().replace("\\","/"))), highlight, suggestion, text)

            if not cmd.split():
                continue
            
            shell.run(cmd.split())
            run += 1

        except KeyboardInterrupt:
            print()


if __name__ == "__main__":
    start = time.time()
    shell = Shell.shell

    try:
        main()

    except Exception:
        cprint(f"[R]A severe error has occured:\n\n")

        print(traceback.format_exc())

        if time.time() - start > 3:
            cprint(f"\n\n[R]Restarting the shell.")
            input("Press enter to restart shell")
            os.chdir(shell.root_path)
            shell.run('modules restart'.split())

        else:
            cprint(f"\n\n[R]A startup error is occuring, restarting the shell has no effect")
            input("Press enter to quit.")
            exit()