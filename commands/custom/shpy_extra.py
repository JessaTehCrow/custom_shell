import re
__desc__ = "Extra buildins for SHPY"
__long_desc__ ="""[R]shpy_extra[P]

Adds other things for the shpy executer"""


shpy = None
def _line(line):
    out = shpy.match_regex('\s*line\s+(\$\S+)',line,"line",True)[0]
    shpy.vars[out] = line

def _vars(line):
    print(shpy.vars)

def _error(line):
    message = shpy.match_regex("^\s*error\s+(\"[^\"]*\")",line,"error",True,True,True)[0]
    raise Exception(message)

def on_ready(self):
    global shpy
    shpy = self.shpy
    shpy.regex.update({
        "line":"\s*line\s+\S+",
        "vars":"\s*vars",
        "error":"\s*error\s+\S+"
    })
    shpy.functions.update({
        "line":_line,
        "vars":_vars,
        "error":_error
    })