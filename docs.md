# Docs

In this file we will be noting the documentation on how to use and make things for this shell.

Contents:
- [Installing](#installing)
- [Shell object](#shell-object)
- [Custom scripts](#custom-scripts)
- [Build-in modules](#build-in-modules)
- Others

## Installing

Honestly, installing is as easy as pie! All you need to do is clone this repository and launch `main.py` in the root directory! All used modules are either build-in or self-supplied
___
## Shell object

The `Shell` object has multiple functionalities, other than just working as a shell.
Your scripts can communicate with the shell object, but it's optional for custom functions.

### Event functions

The shell will run some events to the modules, these consist of `on_load`, `on_ready` and `on_shell_ready`. If a event is not found within the module, it will ignore that event.

#### on_load

`on_load` will be run once this function is imported, the rest of the module might not be fully imported yet, so use this only if you don't need other functions of the module.

The shell will also pass itself as an argument when run.

#### on_ready

`on_ready` will be run when the entire module has finished importing.

The shell will also pass itself as an argument when run.

#### on_shell_ready

`on_shell_ready` will be run when everything has finished initializing.

The shell will also pass itself as an argument when run.

### Getting the object

To get the shell object in any function, it's rather simple.
If the first argument of a functoin is `self` the shell will pass itself as an argument.

Simple example:

```py
def some_custom_function(self):
    print("Got the shell object:",self.__name__) # output: `shell`
```

this is handy if you want to add or use things within the shell object itself.

### Running commands

The shell has a function called `run`, which takes 2 arguments `command` and `help_if_error`.

**Command**
Command is just the command you want to be run in the form of a splitted string.
for example, if you want to run `help example test`, you should pass that as `["help","example","test"]`. 

**help if error**
This is a boolean value, default is `True`. This just runs the help command for the given command (or none if it's a system command). Recommended to set this to false if you're running commands through a function. 

### Module injecting

You can insert certain functions, or classes into the shell, so other modules are able to use them aswell. This can be done fairly easy aswell.

Using the shell object you can do something along the lines of this
```py
# Class definition
class some_class:
    def __init__(self):
        self.some_value = 10

# Class injection
def on_ready(self):
    self.some_name = some_class()
```
Check `json_loader.py` in `/commands/base/` for an example.

___
## Custom Scripts

Custom scripts are fun ;D
___
## Build-in modules

### Json loader

The `Json loader` module inserts itself within the shell, making it accessable using `self.loader` within any module function.
The loader saves all it's settings to `/settings/loader.json`, there you can change the values of sertain things in order to make work / look like you want it to.

#### loader.load()

The `self.loader.load()` has 3 parameters. `default`, `sub` and `_name`. 

**Default**
The `default` parameter is the default value you expect for it. Say if you need a welcome message, you want a default value to be assigned but also want to be customizable within settings.
here's a starting example for the default value. This value will be saved when first loaded, but will be ignored if there is another value defined within the settings.

**Sub**
The `sub` parameter is the sub-catagory which you want to load, this defaults to `main` if no value is given.
This will save and read the value from a sub catagory within the setting, looking something like this:
```json
{
    "some_module":{
        "main":"default location",
        "sub_catagory":"Sub catagory with the name 'sub_catagory'"
    }
}
```

**Name**
The `_name` parameter is a little different from the others.
This value will be auto-assigned to the name of the module it's currently being accessed from.

Lets say you have a module that loads some data from a module named `some_module`. The `_name` parameter will be automatically set to `some_module`.
This auto-assigning can be over-written by forcefully giving the `_name` a string value.

**Example**
Here's a full example on how to use the `loader.load` function:

```py
# Example module name: loader_test

def main(self):
    default_increment = 5
    increment = self.loader.load(default_increment) # defaults: sub = 'main' AND _name = 'loader_test'

    value = 0
    for x in range(10):
        value += increment
        print(value)
```
This example will look for and save in this setting tree (After atleaast 1 initialization):
```json
{
    "loader_test": {
        "main" : 5
    }
}
```
5 being the default value given. You can edit `5` to be anything you want, just try to make sure it's the same data type!
___
#### loader.save()

`loader.save` has the same variables for the same actions as [loader.load](#loader.load()) did.
The only difference is that `loader.save()` will over-write the current value.

___
## Other things that will probably eventually come to mind, hopefully