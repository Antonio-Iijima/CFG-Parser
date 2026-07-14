from config import CONFIG
from main import CONTEXT

import compiler

import PyInstaller.__main__
import cloup
import shutil
import os



@cloup.command(context_settings=CONTEXT)
@cloup.argument("path", type=cloup.Path(exists=True, file_okay=False, resolve_path=True))
@cloup.option_group(
    "Options",
    cloup.option("-i", "--interpreter", "implementation", flag_value="interpreter", help="Compile an interpreter.", default=True),
    cloup.option("-c", "--compiler", "implementation", flag_value="compiler", help="Compile a compiler."),
    cloup.option("-d", "--debug", is_flag=True, help="Run in debug mode."),
    cloup.option("-o", "--onefile", is_flag=True, help="Generate single file executable."),
    cloup.option("-m", "--metacompile", is_flag=True, help="Enable metacompilation (requires BNF-specified language directory input).")
)
@cloup.option_group(
    "Backup Options",
    cloup.option("-b", "--backup", "backup", is_flag=True, help="Backup current BNF compilation files."),
    cloup.option("-r", "--restore", "restore", is_flag=True, help="Restore saved BNF compilation files."),
    constraint=cloup.constraints.mutually_exclusive
)
def main(path: str, implementation: bool, backup: bool, restore: bool, **flags):
    """Compiles a language system from the files provided in PATH."""

    CONFIG.paths.language = path
    CONFIG.language = path[path.rfind("/")+1:]
    CONFIG.implementation = implementation
    CONFIG.flags.update(flags)


    directory = os.path.dirname(__file__)
    base = os.path.join(directory, "compiler")
    save = os.path.join(directory, "compiler/backup")

    if backup:
        print("Backing up files...")
        for file in os.listdir(save):
            shutil.copyfile(os.path.join(base, file), os.path.join(save, file))
            
    if restore:
        print("Restoring files...")
        for file in os.listdir(save):
            shutil.copyfile(os.path.join(save, file), os.path.join(base, file))


    with open(os.path.join(path, "syntax.txt")) as file:
        compiler.evaluate(file.read())

    if CONFIG.flags.onefile:

        PyInstaller.__main__.run([
            "main.py",
            "--onefile",
            f"--name={CONFIG.language}",
            "--add-data", "config.json:."
        ])

        os.system("rm -r build && rm ./*.spec")



if __name__ == "__main__":
    try:
        main()
    finally:
        CONFIG.save()
