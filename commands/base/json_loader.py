import json,os,sys
__long_desc__ = "Honestly no clue"
__desc__ = "Easily save data to drive."

class _loader():
    def __init__(self,shell):
        self._path = shell.root_path+'/settings/loader.json'
        self._shell = shell
        self._json_data = self.__load__()

    def __load__(self):
        "Load json from file"

        def rewrite():
            with open(self._path,"w") as f:
                f.write("{}")
            return {}

        #See if file exist. If not, make it
        if not os.path.exists(self._path):
            return rewrite()

        #attempt to Read data as json
        try:
            with open(self._path,'r') as f:
                return json.load(f)
        except json.decoder.JSONDecodeError:
            return rewrite()

    def get_module(self):
        return sys._getframe().f_back.f_code.co_filename.split('\\')[-1].split('.')[0]

    def load(self,default,sub:str='main',_name:str=None):
        "Returns json data for module, saves default if it doesn't exist"
        module_name = _name or self.get_module()

        #check if module in data and if sub-name in data[module]
        if not module_name in self._json_data or not sub in self._json_data[module_name]:
            self.save(default,sub,_name=module_name)
            return default
        
        data = self._json_data[module_name][sub]
        if type(data) != type(default):
            self.save(module_name,default,sub)
            return default
        
        if isinstance(data,dict):
            data = {**default,**data}
            if not all(x in data.keys() for x in default.keys()):
                self.save(module_name,data,sub)
        
        #return data
        return data
    
    def save(self,default,sub:str="main",_name:str=None):
        "Save data to disk"
        module = _name or self.get_module()

        #Check if module in data
        if not module in self._json_data:
            self._json_data[module] = {}

        self._json_data[module][sub] = default
        
        #Save to disk
        with open(self._path,'w') as f:
            json.dump(self._json_data,f,indent=4)

def on_ready(self):
    self.loader = _loader(self)

def refresh(self):
    "Refresh json data with file"
    self.loader._json_data = self.loader.__load__()
    self.cprint.cprint("[GR]Succesfully refreshed data")