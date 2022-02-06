import os
from utils.shell import command

__desc__ = "Clears screen"

@command("Clears screen")
def main():
    "Clears screen"
    os.system("cls || clear")  
