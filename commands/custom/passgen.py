import random, string
from cprint import *

__desc__ = "Password generator"
__long_desc__ = """[R]passgen[P]

Passgen is a module that helps you generate passwords with different character maps
each character map uses different characters."""

charmaps = {
    'letters': string.ascii_letters,
    'lower':   string.ascii_lowercase,
    'upper':   string.ascii_uppercase,
    'full':    string.ascii_letters + string.punctuation
}

def main(length:int, charmap:str='letters'):
    "Generate a password from a charmap"
    __help__ = "[B]Length [G]is how many characters long the password will be\n[B]Charmap [G]Can be any of: [P]letters[G], [P]lower[G], [P]upper[G], [P]full"

    if charmap.lower() not in charmaps:
        cprint(f'[R]Invalid charmap [E]{charmap}[R]. Please choose any of: [P]{"[R],[P] ".join(x for x in charmaps)}')
        return 1
    
    password = ''.join(random.choice(charmaps[charmap]) for x in range(length))

    cprint(f"\n[GR]Your [Y]{length}[GR] character long password is: [P]{password}\n")