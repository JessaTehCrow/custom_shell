import os,sys,json

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
    false = ['false',0,'n','no','off']
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