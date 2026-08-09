from main import CONTEXT
from utils import *

import compiler

from time import time

import PyInstaller.__main__
import shutil
import cloup
import os



@cloup.command(context_settings=CONTEXT)
@cloup.argument("path", type=cloup.Path(exists=True, file_okay=False, resolve_path=True), required=False)
@cloup.option("-i", "--interpreter", "implementation", flag_value="interpreter", help="Compile an interpreter.", default=True)
@cloup.option("-c", "--compiler", "implementation", flag_value="compiler", help="Compile a compiler.")
@cloup.option("-d", "--debug", is_flag=True, help="Run in debug mode.")
@cloup.option("-v", "--verbose", is_flag=True, help="Allow warning/miscellaneous messages.")
@cloup.option("-t", "--time", is_flag=True, help="Print compilation time.")
@cloup.option("-o", "--onefile", is_flag=True, help="Generate single file executable.")
@cloup.option("-m", "--metacompile", is_flag=True, help="Enable metacompilation (requires BNF-specified language directory input).")
@cloup.option("-r", "--restore", "restore", is_flag=True, help="Restore saved BNF compilation files.")
@cloup.option("-b", "--backup", "backup", is_flag=True, help="Backup current BNF compilation files.")
@cloup.constraint(cloup.constraints.mutually_exclusive, ["onefile", "metacompile"])
@cloup.constraint(cloup.constraints.mutually_exclusive, ["restore", "backup"])
def main(path: str|None, implementation: str, backup: bool, restore: bool, **flags):
    """Compiles a language system from the files provided in PATH."""

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


    CONFIG.flags.update(flags)
    CONFIG.implementation = implementation

    if CONFIG.flags.metacompile:
        if path is not None: print_warnings("ignoring input", {"metacompiling" : [path]})
        path = os.path.join(CONFIG.paths.root, CONFIG.paths.metacompiler)
    if path is None: raise Exception("missing argument 'PATH'. Did you mean to metacompile instead?")
    
    CONFIG.paths.language = path
    CONFIG.language = os.path.basename(path)

    if CONFIG.flags.time: start = time()
    with open(os.path.join(path, "syntax.txt")) as file:
        compiler.evaluate(file.read())
    if CONFIG.flags.time: print(f"Compilation time: {(time() - start)*1000:.7} ms")

    if CONFIG.flags.onefile:

        CONFIG.save()

        PyInstaller.__main__.run([
            "main.py",
            "--onefile",
            f"--name={CONFIG.language}",
            "--add-data", "config.json:."
        ])

        shutil.rmtree("build")
        os.remove(f"{CONFIG.language}.spec")



if __name__ == "__main__":
    try:
        main()
    finally:
        CONFIG.save()
