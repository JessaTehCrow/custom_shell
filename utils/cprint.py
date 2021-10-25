import os,re
os.system("")

class color:
    BL = '\u001b[30m' #black
    G = '\033[90m' #gray
    L = '\033[96m' #light blue
    P = '\033[95m' #purple
    B = '\033[94m' #bold
    GR = '\033[92m' #green
    Y = '\033[93m' #yellow
    R = '\033[91m' #red
    E = '\033[0m\x1b[0m' #clear
    BO = '\033[1m' #bold
    U = '\033[4m'  #underline
    EBG = '\x1b[6;0;0m' #clear bg
    RBG = '\x1b[6;41m' #red bg
    GRBG = '\x1b[6;42m' #green bg
    YBG = '\x1b[6;43m' #yellow bg
    BBG = '\x1b[6;44m' #blue bg
    PBG = '\x1b[6;45m' #purple bg
    LBG = '\x1b[6;46m' #light blue bg
    WBG = '\x1b[6;47m' #White bg
    GBG = '\x1b[1;7;30m' #gray bg
    ERR = '\x1b[6;39;41m' #error

colors = {}

#i made most of this like 2 years ago, no judge pls
for x in color.__dict__:
    if not x.endswith("_"):
        exec(f"colors['[{x}]'] = color.{x}")

def to_regex():
    return f"\[({'|'.join([x for x in color.__dict__ if not x.endswith('_')])})\]"

def cprint(*sentence):
    sentence = ' '.join(sentence)
    for x in colors:
        sentence = sentence.replace(x,colors[x])
    print(sentence + colors["[E]"])

def NEprint(sentence):
    for x in colors:
        sentence = sentence.replace(x,colors[x])
    print(sentence)

def cconvert(sentence):
    for x in colors:
        sentence = sentence.replace(x,colors[x])
    return sentence

def c_tabulate(input_arr:list,headers:list,focus="left",space:int=5,cols:list=None,title_cols:list=None,sort:str=None,sort_key=None):
    if not input_arr: input_arr = [['N/A']*len(headers)]
    sides = {
        "left":"<",
        "middle":"^",
        "right":">"
    }
    #check if color valid and return if is
    def get_col(var):
        valid_list = lambda arr: all([isinstance(x,str) for x in arr])
        if not var: 
            return [["[E]"]]*len(headers)
        if isinstance(var,list):
            new = []
            for x in var:
                if isinstance(x,list) and valid_list(x):  new.append(x)
                elif isinstance(x,str):  new.append([x])
                else: break
            return new
        if isinstance(var,str): 
            return [[var]]*len(headers)
        raise SyntaxError("Invalid color given for c_tabulate")

    #check if side is a valid side (left,middle,right)
    if not any([all([x in sides for x in focus]),(isinstance(focus,str) and focus in sides)]): raise TypeError("Invalid focus")
    # check if input isn't longer than headers
    if len(sorted(input_arr,key=lambda x:len(x))[-1]) > len(headers): raise TypeError(f"Input longer than headers")

    #Check if array needs to be sorted
    if sort and not sort in headers: raise TypeError("Sort key not in header")
    if sort:
        #get index to sort
        index = headers.index(sort)
        #sort
        input_arr = sorted(input_arr,key=lambda x: (sort_key(x[index]) if sort_key else x[index]),reverse=1)

    cols = get_col(cols)
    title_cols = get_col(title_cols)
    side = [sides[x] for x in focus] if isinstance(focus,list) else sides[focus]
    lengths = [0]*len((sorted(input_arr,key=lambda x:len(x),reverse=1) or [[0]*len(headers)])[0])

    #check if color lenghts are as long as headers
    if not all([len(x)==len(headers) for x in [cols,title_cols]]): raise TypeError("Invalid input lengths for colors")
    
    #just get all offsets
    for arr in input_arr+[headers]:
        for i,x in enumerate(arr):
            #remove all colors ([R],[Y],etc)
            if x != None:
                x =  re.sub(to_regex(),'',x)
            else:
                x = ""
            #get longest length of string splited by newline
            length = len(sorted(x.split("\n"),key=lambda x:len(x))[-1])+2
            #save length
            lengths[i] = [lengths[i],length][length > lengths[i]]

    def get_line(array,side,cols):
        out = []
        for line,arr in enumerate(array):
            temp = []
            nlines = sorted([(x.count('\n') if x != None else 0) for x in arr])[-1]

            for i,x in enumerate(arr):
                #get offset
                x = x if x != None else ""
                off = [len(''.join([r.group() for r in re.finditer(to_regex(),string)])) for string in x.split('\n')]
                temp2 = []

                col = cols[i][line%len(cols[i])]
                for o,string in enumerate(x.split('\n')):
                    oper = side[i] if isinstance(side,list) else side
                    #check if to add one space
                    do = (isinstance(side,list) and ((i==0 and oper!="^") or (i>0 and oper !="^" and side[i-1]=="^")) ) or (oper != "^" and i==0)
                    #Check if to remove one space
                    rem = (i!=0 and oper == '^' and (side[i-1] if isinstance(side,list) else side)!='^' )

                    #Format with tabs. {0}{1:%s%s} = "var1 var2" where %s%s is the side and tab
                    string = [""," "][do]+("{0}{1:%s%s}"%(oper,lengths[i]+off[o]-[0,1][rem])).format(col,string)
                    temp2.append(string)

                #Add empty list of strings if this one isn't as long as others (only if newlines exist)
                temp2 += [' '*lengths[i]]*(nlines-len(x.split('\n'))+1)
                temp.append(temp2)
                # temp.append([([" ",""][(side[i] if isinstance(side,list) else side)=="^"]+"{0:%s%d}"%((side[i] if isinstance(side,list) else side),lengths[i]+off[o])).format(string) for o,string in enumerate(x.split('\n'))] + [' '*lengths[i]]*(nlines-len(x.split('\n'))+1))

            out.append( '\n'.join([(' '*space).join(x) for x in list(zip(*temp))]))
        return '\n'.join(out)

    #print
    cprint(get_line([headers],"^",title_cols))
    cprint((' '*space).join((['-',"v"][x==sort])*lengths[i] for i,x in enumerate(headers)))
    # cprint((' '*space).join('-'*(x) for x in lengths))
    cprint(get_line(input_arr,side,cols))