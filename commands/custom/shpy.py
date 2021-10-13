import os,time,cprint,re,json

__desc__ = "Custom bash executer for .spy files"
__long_desc__ = """[R]Shpy[P]

A [R].spy[P] file executer, that runs commands on this shell making automizing common shell commands easier.
Can also do basic language operations."""

class _parser():
    def __init__(self,shell):
        self.regex = {
            "loop":"^\s*loop\s\$\w+\s.*:\n",
            "print":"\s*print\s*.*",
            "wait":"\s*wait\s.+",
            "set_var":"\s*\$.+\s*=",
            "if":"\s*if\s+\n",
            "input":"\s*input\s+\S+",
            "func":"\s*func\s+\w+.*:\n",
            "add":"\s*add\s+(\S+)",
            "is_type":"\s*is_type\s+(\S+)",
            "type":"\s*type\s+\S+",
            "try":'\s*try\s+\S+\n',
            "count":"\s*count\s+(\S+)"
        }
        self.functions = {
            "loop":self.loop,
            "print":self.spy_print,
            "wait":self.wait,
            "set_var":self.set_var,
            "if":self.if_statement,
            "input":self.user_input,
            "func":self.func,
            "add":self.add,
            "is_type":self.is_type,
            "type":self.get_type,
            "try":self.try_code,
            "count":self.count
        }
        self.callable = {}
        self.vars = {}
        self.indent = [x[:-1] for x in self.regex.values() if x.endswith('\n')]
        self.funcs = [x[:-1] if x.endswith('\n') else x for x in self.regex.values()]
        self.shell = shell

    #-------------- Buildin functions -----------------#

    def try_code(self,line):
        out = self.match_regex("\s*try\s+(\$\S+):",line,"try",True)[0]
        backup = dict(self.vars)
        try:
            self.run_lines(line)
        except Exception as e:
            backup[out] = str(e)
            self.vars = backup

    def if_statement(self,line):
        tv1,op,tv2 = self.match_regex("\s*if\s+(\$\w+|[\[][^\[\]]*[\]]|\"[^\"]*\"|true|false|[+-]?\d*[\.]?[\d]+)\s+(==|!=|>=|<=|<|>)\s+(\$\w+|[\[][^\[\]]*[\]]|\"[^\"]*\"|true|false|[+-]?\d*[\.]?[\d]+):",line,"if",True, replace_litteral=True)

        _,v1 = self.find_type(self.var_replace_litteral(tv1))
        _,v2 = self.find_type(self.var_replace_litteral(tv2))

        if not all([v1!=None,v2!=None]):  raise SyntaxError(f"Invalid if statement : \n[Y]{self.code[line]}")
        if op in ["==","!="] or any([type(x)==bool for x in [v1,v2]]):
            e = {"==":v1==v2,"!=":v1!=v2}
        else:
            v1 = v1 if type(v1)in [int,float] else len(v1)
            v2 = v2 if type(v2)in [int,float] else len(v2)
            e = {"==":v1==v2,"!=":v1!=v2,"<=":v1<=v2,">=":v1>=v2,"<":v1<v2,">":v1>v2}

        if not op in e: raise SyntaxError(f"Invalid operator for if statement : \n[Y]{self.code[line]}")
        if not e[op]: return
        torun,_ = self.check_index(line)
        for x in torun: 
            e = self.run_line(x)
            if e and self.get_index(line)==0: raise SyntaxError(f"Invalid {e[0]} in If statement")
            elif e: return e

    def func(self,line):
        name,vars = self.match_regex("\s*func\s+(\w+)\s+(\$.*)\s*:",line,"function",True)
        vars = re.findall("\$[a-zA-Z\d]+",vars)
        torun,_ = self.check_index(line)
        self.callable[name] = [line,vars,torun]

    def is_type(self,line):
        raw = self.code[line]
        valid = ["string","bool","number","list"]
        out,val1,val2 = self.match_regex("\s*is_type\s+(\$\S+)\s+([\"][^\"]*[\"]|\$\S+)\s+(\$\w+|[\[][^\[\]]*[\]]|\"[^\"]*\"|true|false|[+-]?\d*[\.]?[\d]+)",line,"is_type",True)
        _,var1 = self.find_type(self.var_replace_litteral(val1))
        type1,var2 = self.find_type(self.var_replace_litteral(val2))
        if type(var1) != str: raise SyntaxError(f"Invalid input. Must be string : \n[Y]{raw}")
        if not var1 in valid: raise SyntaxError(f"Unknown input, must be `string`,`bool`,`number` or `list`")
        self.vars[out] = type1 == var1

    def get_type(self,line):
        out,val1 = self.match_regex("\s*type\s+(\$\S+)\s+(\$\w+|[\[][^\[\]]*[\]]|\"[^\"]*\"|true|false|[+-]?\d*[\.]?[\d]+)",line,"type",True)
        name,_ = self.find_type( self.var_replace_litteral( val1 ) )
        if not name: raise SyntaxError(f"Value not any type")
        self.vars[out] = name

    def add(self,line):
        raw = self.code[line]
        valid = [['string','string'],['number','number'],['list','string'],['list','number'],['list','bool']]
        out,val1,val2 = self.match_regex("\s*add\s+(\$\S+)\s+(\$\w+|[\[][^\[\]]*[\]]|\"[^\"]*\"|true|false|[+-]?\d*[\.]?[\d]+)\s+(\$\w+|[\[][^\[\]]*[\]]|\"[^\"]*\"|true|false|[+-]?\d*[\.]?[\d]+)",line,"add",True)
        type1,var1 = self.find_type( self.var_replace_litteral(val1) )
        type2,var2 = self.find_type( self.var_replace_litteral(val2) )
        if not [type1,type2] in valid and not [type2,type1] in valid: raise SyntaxError(f"Invalid add types '{type1}' and '{type2}'")
        if not [type1,type2] in valid: 
            type1,type2 = type2,type2
            var1,var2 = var2,var1
        if type1 == 'list': var1.append(var2)
        else: var1 += var2
        self.vars[out] = var1

    def set_var(self,line):
        varname,tvalue = self.match_regex("^\s*(\$\S+)\s*=\s*(\$\w+|[\[][^\[\]]*[\]]|\"[^\"]*\"|true|false|[+-]?\d*[\.]?[\d]+)",line,"Variable",True)
        _,value = self.find_type( self.var_replace_litteral(tvalue) )
        # if value==None: raise SyntaxError(f"Syntax error : \n{self.code[line]}") <- Unsure if i can remove this line
        self.vars[varname] = value
    
    def count(self,line):
        valid = ["string","list"]
        out,inp = self.match_regex("\s*count\s+(\$\S+)\s+(\$\w+|[\[][^\[\]]*[\]]|\"[^\"]*\")",line,"count",True)
        vtype,var = self.find_type( self.var_replace_litteral(inp) )
        # if not vtype in valid: raise SyntaxError(f"Invalid input type ({vtype}) : \n[Y]{self.code[line]}") <- Unsure if i can remove this line
        self.vars[out] = len(var)

    def user_input(self,line):
        varname,text = self.match_regex("\s*input\s+(\$\S+)\s+([\"].*[\"]|\$\S+)",line,"input",True)
        text = self.get_string( self.var_replace_litteral(text) )[0]
        # if not text: raise SyntaxError(f"Invalid input : \n[Y]{raw}")  <- Unsure if i can remove this line
        self.vars[varname] = input(cprint.cconvert('[E]'+text)).replace('"',"'")

    def loop(self,line):
        valid,stop = ["number","list"],False
        out,inp = self.match_regex("\s*loop\s+(\$\S+)\s+(\$\S+|[\[][^\]]*[\]]|\"[^\"]*\"|true|false|[+-]?\d*[\.]?[\d]+):",line,"loop",True)
        vtype,am = self.find_type(self.var_replace_litteral(inp))
        am = am if vtype=='list' else range(am)
        if not vtype in valid: raise SyntaxError(f"Invalid loop input ({vtype}) : [Y]\n{self.code[line]}")
        torun,_ = self.check_index(line)
        for itr in am:
            if stop:break
            self.vars[out] = itr
            for x in torun: 
                if stop: break
                e = self.run_line(x)
                if e and e[0] == 'break': stop=True
                elif e and e[0]=='return' and self.get_index(line) == 0: raise SyntaxError("Return outside of a function")
                elif e and e[0] in ["return","breakall"]: return e

    def spy_print(self,line):
        def unescape(text):
            return text.encode('latin1', 'backslashreplace').decode('unicode-escape')
        temp = self.get_string(self.var_replace(self.code[line]))
        if not all(temp): raise SyntaxError(f"Invalid print. Did you enclose it in quotes? : [Y]\n{self.code[line]}")
        text = ' '.join( temp ) if temp else ""
        cprint.cprint("[E]"+unescape(text))

    def wait(self,line):
        amount = self.get_number( self.var_replace(self.code[line]) )
        if not amount or len(amount) >1: raise SyntaxError(f"No valid value given for wait: {self.code[line]}")
        time.sleep(amount[0])

    #--------------------------------------------------#

    def run_lines(self,line):
        torun,_ = self.check_index(line)
        for l in torun:
            self.run_line(l)

    def find_type(self,string):
        all_types = [["list",self.get_list],["string",self.get_string],['bool',self.get_bool],['number',self.get_number]]
        temp = [[n,f(string)[0]] for n,f in all_types if f(string)[0]!=None and len(f(string))==1]
        if not temp: return [None,None]
        return temp[0]

    def var_replace(self,string):
        text = str(string)
        items = [[k,v] for i,(k,v) in enumerate(self.vars.items())]
        items = sorted(items, key = lambda x: len(x[0]),reverse=True)
        for k,v in items:
            new = str(v) if type(v) != bool else str(v).lower()
            text = text.replace(k,new)
        return text
    
    def var_replace_litteral(self,string):
        text = str(string)
        items = [[k,v] for i,(k,v) in enumerate(self.vars.items())]
        items = sorted(items, key = lambda x: len(x[0]),reverse=True)

        for k,v in items:
            new = (f'"{v}"' if type(v)==str else json.dumps(v)) if type(v) in [str,list] else (str(v) if type(v) != bool else str(v).lower())
            text = text.replace(k,new)
        return text

    def get_bool(self,line):
        raw = self.code[line] if type(line)==int else line
        temp = re.findall("(true|false)",raw)

        if not temp: return [None]
        return [x == 'true' for x in temp]
 
    def get_string(self,line):
        raw = self.code[line] if type(line).__name__ == 'int' else line
        temp = re.findall("\".*?\"",raw)
        if not temp: return [None]
        text = [self.var_replace(x[1:][:-1]) for x in temp]
        return text

    def get_list(self,line):
        raw = self.code[line] if type(line).__name__ == 'int' else line
        temp = re.findall("\[.*\]",raw)
        if not temp: return [None]
        for i,x in enumerate(temp):
            x = self.var_replace(x)
            temp[i] = re.sub("([,\[])\s*(True)\s*([,\]])",r"\1true\3",x)
            temp[i] = re.sub("([,\[])\s*(False)\s*([,\]])",r"\1false\3",temp[i])
        arr = [json.loads( x ) for x in temp]
        return arr
    
    def get_number(self,line):
        raw = self.code[line] if type(line).__name__ == 'int' else line
        temp = re.findall('[+-]?\d*[\.]?[\d]+',self.var_replace_litteral(raw))
        if not temp: return [None]
        if any(['.' in x for x in temp]):
            num = [float( x ) for x in temp]
        else:
            num = [int( x ) for x in temp]
        return num

    def valid_indent(self,line):
        temp = self.code[line]
        return any([re.match(r,temp) for r in self.indent])

    def run_callable(self,func,line):
        _,vars,torun = self.callable[func]
        raw,output = self.code[line],None
        in_vars = re.findall("\$\w+|[\[][^\[\]]*[\]]|\"[^\"]*\"|true|false|[+-]?\d*[\.]?[\d]+",raw[len(func)+1:])
        if not len(in_vars) in [len(vars),len(vars)+1]: raise SyntaxError(f"Not enough or too many variables for function : \n[Y]{raw}")
        if len(in_vars) == len(vars)+1:
            output = in_vars[0]
            in_vars.pop(0)
        if not output == None and not re.match('\$\w+',output): raise SyntaxError(f"Invalid function output variable : \n[Y]{raw}")
        backup = dict(self.vars)
        for name,val in zip(vars,in_vars):  self.vars[name] = self.find_type( self.var_replace_litteral(val) )[-1]
        for x in torun:
            e = self.run_line(x)
            if e:
                if e[0] in ['break','breakall'] and not 'loop' in self.code[x]: raise SyntaxError(f"Invalid {e} in function")
                if e[0] == 'return' and len(e[1]) != 1: raise SyntaxError(f"Invalid return")
                elif e[0] == 'return': 
                    _,val = self.find_type(self.var_replace(e[1][0]))
                    if not val: raise SyntaxError(f"Invalid return")
                    backup[output] = val
                    break

        self.vars = backup
                
    def is_function(self,line):
        temp = self.code[line]
        for i,(k,v) in enumerate(self.regex.items()):
            if re.match(v[:-1] if v.endswith('\n') else v,temp): return k
        return False

    def is_callable(self,line):
        temp = self.code[line]
        for func in self.callable:
            if re.match(f"\s*{func}\s+(\S+)",temp):  return func
        return False

    def match_regex(self,regex,line,name,groups=False,replace=False,replace_litteral=False):
        raw = self.code[line]
        temp = re.match(regex,raw if not replace else (self.var_replace(raw) if not replace_litteral else self.var_replace_litteral(raw) ))
        if not temp: raise SyntaxError(f"Invalid {name} syntax : [Y]\n{raw}")
        if groups: return temp.groups()
        return temp

    def get_index(self,line):
        return re.match("^\s*",self.code[line]).span()[-1]

    #Recursive funcion
    def check_index(self,line):
        # print("-"*50)
        base = line+1
        indent = self.get_index(line) if line == 0 else self.get_index(line+1)
        skip,torun,total = 0,[],-1

        for l,c in enumerate(self.code[line+1:]):  
            l,total = line+l+1,total+1
            temp = self.get_index(l)
            
            if skip!=0: 
                skip -= 1 if skip else 0
                continue
            if temp == indent:  pass
            elif temp <= indent and indent != 0: return torun,total
            elif temp > indent and self.valid_indent(l-1):
                skip += self.check_index(l-1)[1]-1
                continue
            else: raise SyntaxError(f"Invalid indent : [Y]\n{c}")

            # print(base,c,sep=' -> ')
            torun.append(l)
        return torun,total+1
    
    def is_special(self,line):
        raw = self.code[line]
        regex = {"breakall":"\s*breakall","break":"\s*break","return":"\s*return"}
        for i,(k,v) in enumerate(regex.items()):
            if re.search(v,raw): 
                if self.get_index(line) == 0: raise SyntaxError(f"{k} outside of it's use: \n[Y]{raw}")
                return [k,re.findall("\$\w+|[\[][^\[\]]*[\]]|\"[^\"]*\"|true|false|[+-]?\d*[\.]?[\d]+",raw)]
        return False

    def run_line(self,line):
        func = self.is_function(line)
        callable = self.is_callable(line)
        is_special = self.is_special(line)
        if callable:  self.run_callable(callable,line)
        elif func:  return self.functions[func](line)
        elif is_special: return is_special
        else: self.shell.run(self.var_replace(self.code[line]).split())

    def run(self,code):
        self.code = code
        try:
            e,_ = self.check_index(0)
        except Exception as e:
                cprint.cprint(f"[R]{e}")
                return

        for x in e: 
            try:
                self.run_line(x)
            except Exception as e:
                cprint.cprint(f"[R]{e}")
                break
        self.vars = {}
        self.callable = {}
        self.code = None

def on_ready(self):
    parser = _parser(self)
    self.shpy = parser

def main(self,file:str):
    "Run a batch based tytpe thing"
    file = file if file.endswith('.spy') else file+'.spy'
    if os.path.isfile(file):
        code = [""] + [x for x in open(file).read().splitlines() if bool(x.strip())]
        parser = self.shpy
        parser.run(code)
    else:
        cprint.cprint(f"[R]File doesn't exist")