import os

__desc__ = "Directory listing"

if os.name == 'nt':
    try:
        import win32api, win32con
        succes = True
    except:
        print("Unable to load script. (missing 'pypiwin32', can be installed with 'pip install pypiwin32')")


colors = {
    "file":"[Y]",
    "directory":"[GR]",
    "hidden_file":"[L]",
    "hidden_directory":"[R]",
    "executable":"[B]"
}

class node:
    def __init__(self,name):
        self.name = name
        self.hidden = self.get_hidden()
        self.type = self.get_type()
        self.executable = self.get_executable()
        self.color = colors['executable'] if self.executable else colors[self.type]

    def get_type(self):
        new_type = "directory" if os.path.exists(self.name+"/") else "file"
        new_type = new_type if not self.hidden else "hidden_"+new_type
        return new_type

    def get_hidden(self):
        if os.name == 'nt':
            attribute = win32api.GetFileAttributes(self.name)
            return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
        else:
            return self.name.startswith('.')

    def get_executable(self):
        if "file" in self.type and os.name != "nt":
            return os.access(self.name, os.X_OK)

        return False

def main(self):
    cprint = self.cprint.cprint
    "Directory listing"
    offset = 50
    raw = os.listdir()

    listing = {
        "file":[],
        "directory":[],
        "hidden_file":[],
        "hidden_directory":[]
    }

    for x in raw:
        offset = len(x)+6 if len(x) > offset else offset

        new = node(x)
        listing[new.type].append(new)

    def get_color(name):
        return [x for x in colors if x[:-1] in name and x.startswith(name[0])][0]

    def print_names(name1,name2):
        col1,col2 = get_color(name1),get_color(name2)
        names = [name1,name2] if len(listing[col1]) > len(listing[col2]) else [name2,name1]
        col1 = colors[get_color(names[0])]
        col2 = colors[get_color(names[1])]

        cprint(f"[G]__[ {col1}{names[0]}" + " "* (offset-len(names[0])+1) + f"[G]__[ {col2}{names[1]}" )
        cprint(f" [G]|" + ' '*(offset+3) + ' |')

    def output(ar1,ar2):
        array = [ar1,ar2] if len(ar1) > len(ar2) else [ar2,ar1]
        lar2 = len(array[1])

        for x in range(len(array[0])):
            ob1 = array[0][x]
            out = f" [G]|-[ {ob1.color}{ob1.name}"

            if x < lar2:
                ob2 = array[1][x]
                toff = offset - len(ob1.name)
                out += " "*toff + f" [G]|-[ {ob2.color}{ob2.name}"
            cprint(out)
        print()

    print_names("files","directories")
    output(listing['file'],listing['directory'])

    if any([len(x) > 0 for x in [listing['hidden_file'],listing['hidden_directory']]]):
        print_names("hidden_files","hidden_directories")
        output(listing['hidden_file'],listing['hidden_directory'])
