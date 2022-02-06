from utils.shell import command
import os

__desc__ = "Clears screen"

@command("Clears screen")
def main():
    os.system("cls || clear")  
