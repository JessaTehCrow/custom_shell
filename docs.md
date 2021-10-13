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
Your scripts can communicate with the shell object. [Add more here]
___
## Custom Scripts

Custom scripts are fun ;D
___
## Build-in modules

### Json loader

The `Json loader` module inserts itself within the shell, making it accessable using `self.loader` within any module function.
The loader saves all it's settings to `/settings/loader.json`, there you can change the values of sertain things in order to make work / look like you want it to.

### loader.load()

The `self.loader.load()` has 3 parameters. `default`, `sub` and `_name`. 

**Default**
The `default` parameter is the default value you expect for it. Say if you need a welcome message, you want a default value to be assigned but also want to be customizable within settings.
here's a starting example for the default value. This value will be saved when first loaded, but will be ignored if there is another value defined within the settings.
```py
def main(self):
    default_message = "Hello there!"
    # To be continued
```

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
        "main" : 5 // 5 being the default value given. You can edit `5` to be anything you want, just try to make sure it's the same data type!
    }
}
```
___
### loader.save()

`loader.save` has the same variables for the same actions as [loader.load](#loader.load()) did.
The only difference is that `loader.save()` will over-write the current value.

___
## Other things that will probably eventually come to mind, hopefully