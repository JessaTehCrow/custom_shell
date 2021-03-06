import subprocess, os

from subprocess import DEVNULL
from utils.shell import command, event, Shell
from utils.cprint import cconvert, cprint

@command("Check for update")
def check(self:Shell):
    current_dir = os.getcwd()
    os.chdir(self.root_path)

    try:
        raw_current_hash = subprocess.check_output('git rev-parse HEAD', stderr=DEVNULL)
        raw_latest_hash = subprocess.check_output('git ls-remote https://github.com/JessaTehCrow/custom_shell.git', stderr=DEVNULL)

        subprocess.check_call('git fetch', stdout=DEVNULL, stderr=DEVNULL)

        current_hash = raw_current_hash.decode()[:-1]
        latest_hash = raw_latest_hash.decode().split()[0]

        info = subprocess.check_output(f'git show {latest_hash} --stat').decode()

    except Exception as e:
        print(e)
        return 2

    self.version_hash = current_hash

    if current_hash == latest_hash:
        cprint("\n[E]Shell is up to date!\n")
        return


    cprint("\n[Y][U]There's a new update available, do you want to update?[E]\n")
    cprint(f"[G]Current hash: [E]{current_hash}")
    cprint(f"[G]New hash: [E]{latest_hash}\n")

    print('\n')
    print(info)
    print('\n')

    update = input(cconvert(" [GR]y [G]/ [R]n [G]> [P]"))

    if update.lower() in "y yes ye".split():
        cprint(f"[E]Pulling update...")

        try:
            output = subprocess.check_output('git pull', stderr=DEVNULL)
            output.decode()
        except Exception as e:
            cprint(f"[R]There was a problem during the shell update:\n\n")
            print(e)
        
        self.run(['clear'])
        self.run('modules restart'.split())
    
    cprint('[G]Not updating')
    os.chdir(current_dir)

@event("on_shell_ready")
def test(self):
    
    check_update = self.loader.load(True, "do_update")

    if not check_update:
        cprint("[E]Update check is turned off")
        return

    check(self)


@command("Set update check on or off")
def set(self, value:bool):
    self.loader.save(value, "do_update")

    if value:
        cprint(f"\n[E]The shell will now check if there's an update on start up!\n")
    else:
        cprint(f"\n[E]The shell will no longer check if there's an update!")
        cprint(f"[G](You might miss a bug fix update)\n")
