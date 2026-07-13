from config import CONFIG
from main import CONTEXT

import compiler

import PyInstaller.__main__
import click
import shutil
import os


@click.command(context_settings=CONTEXT)
@click.argument("path", type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option("-i", "--interpreter", "implementation", flag_value="interpreter", help="Compile an interpreter.", default=True)
@click.option("-c", "--compiler", "implementation", flag_value="compiler", help="Compile a compiler.")
@click.option("-o", "--onefile", "onefile", is_flag=True, help="Generate single file executable.")
@click.option("-b", "--backup", "backup", is_flag=True, help="Backup current BNF compilation files.")
@click.option("-r", "--restore", "restore", is_flag=True, help="Restore saved BNF compilation files.")
@click.option("-m", "--metacompile", "metacompile", is_flag=True, help="Enable metacompilation (requires BNF-specified language directory input).")
def main(path: str, implementation: bool, onefile: bool, backup: bool, restore: bool, metacompile: bool):
    """Compiles a language system from the files provided in PATH.
    
    NB - if `-b` and `-r` are used together, the backup happens BEFORE the restoration, leaving the current primary files unchanged."""


    CONFIG.paths.language = path
    CONFIG.language = path[path.rfind("/")+1:]
    CONFIG.implementation = implementation
    CONFIG.flags.metacompile = metacompile

    directory = os.path.dirname(__file__)
    base = os.path.join(directory, "compiler")
    backup = os.path.join(directory, "compiler/backup")


    if backup:
        print("backing up files")
        for file in os.listdir(backup):
            shutil.copyfile(os.path.join(base, file), os.path.join(backup, file))
            
    if restore:
        print("restoring files")
        for file in os.listdir(backup):
            shutil.copyfile(os.path.join(backup, file), os.path.join(base, file))

    with open(os.path.join(path, "syntax.txt")) as file:
        compiler.evaluate(file.read())

    if onefile:

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
