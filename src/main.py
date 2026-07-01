from utils import get_config, set_config, get_input
from lalr import LALR_Parser

import processing

import click
import sys
import os

from time import time



BUNDLED = (getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'))


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
def cli(): pass



@cli.command(hidden=BUNDLED)
@click.argument("path", type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option("-i", "--interpreter", "implementation", flag_value="interpreter", help="Compile an interpreter.", default=True)
@click.option("-c", "--compiler", "implementation", flag_value="compiler", help="Compile a compiler.")
def compile(path: str, implementation: bool):
    """Compiles a language system from the files provided in PATH."""

    if BUNDLED: return print("Cannot compile from bundled language.")

    cfg = get_config()

    cfg["paths"]["language"] = "/".join(path.split("/")[-2:])
    cfg["language"] = path.split("/")[-1]
    cfg["implementation"] = implementation

    set_config(cfg)

    processing.compile()



@cli.command
@click.argument("input", nargs=-1)
@click.option("-o", "--output", default=get_config("output"), hidden=(get_config("implementation")=="interpreter"), help="Name for output file.", show_default=True)
@click.option("-i", "--interactive", is_flag=True, hidden=(get_config("implementation")=="compiler"), help="Run in interative mode.")
@click.option("-d", "--debug", is_flag=True, help="Run in debug mode.")
@click.option("-f", "--force", is_flag=True, help="Force recompilation.")
@click.option("-x", "--clear", is_flag=True, help="Delete cached compiled files.")
def run(input: tuple, **flags):
    """Runs a compiled language with OPTIONS."""

    cfg = get_config()

    cfg["input"] = list(input) # stored in config as a list
    cfg["output"] = flags.pop("output")
    cfg["flags"] = flags

    isModified = not (cfg == get_config())

    set_config(cfg)
    

    print(f"magicc v{cfg["version"]} </> {cfg["language"]} {cfg["implementation"]}")


    if cfg["flags"]["clear"]:
        for filename in ("AST.py", "eval.py"):
            if os.path.exists(filename):
                os.remove(filename) or print(f"Removed {filename}")
            else:
                print(f"{filename} not found")
        quit()


    if cfg["flags"]["force"] or isModified:
        processing.compile()


    from eval import process


    for filename in input:
        with open(filename) as file:
            process(file.read())

    if cfg["flags"]["interactive"]:
        for line in iter(lambda: get_input("</> "), "quit"):
            if line.strip():
                if cfg["flags"]["debug"]: start = time()
                process(line)
                if cfg["flags"]["debug"]: print(f"Runtime: {time() - start}")    



@cli.command
@click.argument("tests", type=int, nargs=-1)
def test(tests):
    """Run specified built-in test cases; if none are specified, run all available. 
    Recompiles before testing (except if locked)."""
    
    if get_config("implementation") == "compiler":
        return print("No test cases for compiled languages.")


    processing.compile()

    from tests import test

    cfg = get_config()
    cfg["tests"] = tests
    set_config(cfg)
    
    test(tests)



if __name__ == "__main__":
    cli()
