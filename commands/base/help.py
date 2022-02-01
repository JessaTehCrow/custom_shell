__desc__ = "Get help about modules"

def main(self,module:str=None,function:str=None):
    cp = self.cprint
    cprint = cp.cprint
    c_tabulate = cp.c_tabulate

    "Shows help for function"
    __help__ = "[B]module [G]is either a [L]buildin command[G], or a [GR]module[G].\nIf [B]function[G] is used, [B]module [G]needs to be a [GR]module[G], and [B]function [G]a [L]Command[G] within the module."

    title = "[B]"
    def print_funcs(array, long_desc:str = None):
        if long_desc: cprint("[P]" + long_desc + '\n')

        funcs = []
        for x in array: 
            funcs.append([x.name,f"{x.desc or '[BL]'}"])
        cols = [["[L]","[B]"],["[R]",'[P]']]
        c_tabulate(funcs,headers=["Command","Description"],cols=cols,title_cols=title)

    def load_args(function):
        cols = ['[E]',"[GR]",'[R]']
        inbt = ["","[E]:","[E]="]
        out = []
        for i,arg in enumerate(function.args):
            temp = ""
            for it,det in enumerate(arg):
                if det == None or det=="None": break
                det = det if it<len(arg)-1 else repr(det)
                temp += f"{inbt[it]}{cols[it]}{det}"
            out.append(['','\n'][(i)%3==0 and i !=0 and len(function.args)>i] + temp)
        return "[E]" + '[G], '.join(out)

    def print_detailed_help(function):
        args = load_args(function)
            
        data = [[function.name,args,str(function.help or function.desc or '[BL]')]]
        cols = [["[L]"],["[E]"],["[P]"]]
        c_tabulate(data,headers=["Name","Args\n([E]name:[GR]type[E]=[R]default[B])","Description"],focus=["middle","middle","left"],cols=cols,title_cols=title)

    modules = [x for x in self.commands][1:]

    if not any([module, function]):
        cprint(f"\n[Y]Modules\n")
        funcs2 = [[x,self.commands[x]['description']] for x in modules]
        funcs = [[name,(desc or "")] for name,desc in funcs2]
        cols = [["[L]","[B]"],["[R]","[P]"]]
        c_tabulate(funcs,headers=["Name","Description"],cols=cols,title_cols=title)

    elif module and not function:
        if not module in self.commands and not module in self.commands['pre']: 
            cprint(f"[R]Module not found")
            return 2
        if module in self.commands:
            print_funcs([val for key,val in self.commands[module].items() if not key in ['description','long_description']],self.commands[module]['long_description'])
        else:
            print_detailed_help(self.commands['pre'][module])

    else:
        if not module in self.commands or not function in self.commands[module]:
            cprint(f"[R]Module or Function not found")
            return 2
        print_detailed_help(self.commands[module][function])
    print()        
