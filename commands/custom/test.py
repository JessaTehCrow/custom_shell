__desc__ = "Just a test lol"
__long_desc__ = """[R]test[P]

Just a test, really"""

def test(self):
    "Just a test lol"
    
    def run_command(command):
        cprint(f"[Y]Running command [B]{command}")
        exit_code = self.run(command.split(), help_if_error=False)

        if not exit_code:
            cprint(f"\n[GR]Command ran without problems!")
        else:
            cprint(f'\n[R]There was a problem running the command')

    cprint = self.cprint.cprint
    commands = [
        "Some command that will error",
        "help custom command that will also error",
        "calc 32*145",
        "ping google.com -n 1"
    ]

    for x in commands:
        print('-'*20)
        run_command(x)
        print()