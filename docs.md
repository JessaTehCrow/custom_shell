# Docs

In this file we will be noting the documentation on how to use and make things for this shell.

Contents:
- [Installing](#installing)
- [Shell object](#shell-object)
- [Custom modules](#custom-modules)
- [Build-in modules](#build-in-modules)
- [Cprint](#cprint)
- [Settings](#settings)
- Others

## Installing

Honestly, installing is as easy as pie! All you need to do is clone this repository and launch `main.py` in the root directory! All used modules are either build-in or self-supplied
___
## Shell object

The `Shell` object has multiple functionalities, other than just working as a shell.
Your scripts can communicate with the shell object, but it's optional for custom functions.

### Usable functions

The shell has 1 function you can use, `run`

**Run**
The shell has a function called `run`, which takes 2 arguments `command` and `help_if_error`.

`command` is just the command you want to be run in the form of a splitted string.
for example, if you want to run `help example test`, you should pass that as `["help","example","test"]`. 

`help_if_error` is a boolean value, default is `True`. This just runs the help command for the given command (or none if it's a system command). Recommended to set this to false if you're running commands through a function. 

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
## Custom Modules

Custom modules are easy to make with this shell.

### Getting started

The first step to make your own module, is to make a new file.
This file should be made in `commands/custom/`. You can name it anything you want (but you should make sure it's not already used, in `commands/base`). It's file extention has to be `.py`.

For example: `new_module.py`.

Once you made this, you can use the command `refresh` to load it into the shell. Once it's loaded, you can reload the module using the command `reload [module name]`.

### Code

**Base**
To make a functional command, all you need to do is add a function to it.
```py
# new_module.py

def new_command():
    print("Command works!")
```
After adding the function, you can reload the module and then you can run the command as such: `new_module new_command`, and it'll run!

**Arguments**
Adding arguments to your commands work the exact same way with normal functions. 

The only difference is that if you use type-hinting for the arguments, the shell will check if those arguments fit the type hints, and will automatically change the argument into the type.

so if i have a function like this:
```py
def double(number : float):
    print(f"The double of {number} is {number*2}")
```
and run it like you would with other commands (`module double 30`), it'll automatically feed number as a float, so you don't have to cast it to the type yourself.

**Returns**
All functions used by the shell have an exit code, this is either `0`, `1` or `2`

An exit-code of `0` means there was no problem running the command, this is also the default code for if your function does not return any of them.

An exit code of `1` means that there was a problem running the command, and is user-error, which will cause the shell to print the hell for that function (Unless `help_if_error` is set to false).

An exit code of `2` means that there was something wrong, but the help will not be shown. Usefull for if there went something wrong that the user couldn't do anything about (For example: Failing to ping a host)

**help & description**
All functions should have a help and a description. Fortunately the build in help-command does most of the work for the help section.


The shell will read all functions within a module, and will look at the name, arguments and argument type-hints. From this it'll generate a easy to read over-view of the function.

The help will still need a user-defined help description however.
This can be added by making a variable named `__help__` within the function. 
```py
def some_example(number : int):
    __help__ = "The variable 'number' is a integer"
    print(number*number)
```
This will be added to the detailed help section automatically aswell.
(The detailed help is only shown if a specific function is given. For example `help module function`)

Adding a description is the same as adding a description to a function normally is. This will be shown with the module help. for example `help module` as well as with the detailed help.

```py
def some_example(number : int):
    """Prints the input number squared"""

    __help__ = "The variable 'number' is a integer"
    print(number*number)
```
this would be the final version of the function.
Like stated before, you don't need to check if number is actually an integer, the shell takes care of that.

___
## Build-in modules

### Json loader

The `Json loader` module inserts itself within the shell, making it accessable using `shell.loader` within any module function.
The loader saves all it's settings to `/settings/loader.json`, there you can change the values of sertain things in order to make work / look like you want it to.

#### loader.load()

The `shell.loader.load()` has 3 parameters. `default`, `sub` and `_name`. 

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
## Cprint

The cprint is the build-in coloring method you can access through the shell object (`shell.cprint`), or through importing it from `utils.cprint`.

- Coloring
- Cprint
- Cconvert
- NEprint
- C tabulate
- Colors

### Coloring

This module has an easy way of coloring text, it's by using `[color code here]` within the string.
For example `"[R]This is red. [B]This is blue. [Y]This is yellow`. 

All the colors can be found [below](#colors)

### Cprint

This is the main way of printing colored text. It works the same as normal `print` except it colors the color-coded string. 
This will also automatically stop the color at the end of the string (This may break if an Error occured within your program).

### Cconvert

This is the way to store a colored string as a variable, and can be used in other functions like `input` or even normal `print`

`colored_text = cprint.cconvert("[R]Colored [Y]String")`


### NEprint

This is the same as [cprint](#cprint) except it does not clear the color at the end.

### C tabulate

This is a slightly more complex function, but still easy to use (i think...)

`c_tabulate` has 8 arguments `input_array`, `headers`, `space`, `colors`, `title_colors`, `sort` and `sort_key`.

`input_array` and `headers` are neccecary and the rest are optional.

**C_Tabulate example**
```
     Title1             Title2         Title3
----------------     ------------     ---------
 Ctabulate            Test             Example
                      < Was none
 Only one value
 ```
Example above can be replicated with this code
 ```py
def main(self):
    cprint = self.cprint

    headers = ["Title1", "Title2", "Title3"]

    inp = [
        ["Ctabulate","Test","Example"],
        [None,"< Was none"],
        ["Only one value"]
    ]

    cprint.c_tabulate(inp,headers)
 ```

**input_array**

`input_array` is a 2d matrix (or simply put, an array of arrays).
This matrix can be as long as you want, however the arrays within that matrix need to be as long as the headers, but can be shorter.
Nonetypes will be percieved as an empty value, and will also be treated that way. (See ctabulate example above)



**headers**

The headers are the headers shown on the list

### Colors

`[E]` = Clear color

`[BL]` = Black

`[G]` = Gray

`[GR]` = Green

`[B]` = Blue

`[L]` = Light blue

`[P]` = Purple

`[R]` = Red

`[Y]` = Yellow

`[BO]` = Bold

`[U]` = Underline

To change a color into a background color, all you need to do is add `BG` to it.
For example `[RBG]` is red background.

## Settings

There's only one settings that this shell comes with by default, that's the `shell` setting. This is what prompt you get when using the shell. aka: `C:/path/to/where/you/are Name> ` or `user$ `.
This uses the cprint coloring method and has one variable you can use within it.
You can use `%dir%` to put your current working directory in that place.

For example, if you have the shell setting like this: `(%dir%) name> `, it's visible output would be something along the lines of: `(C:/current/working/directory) name> `.

## Other things that will probably eventually come to mind, hopefully