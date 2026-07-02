from utils import *

import processing

import click
import os

from time import time



CONTEXT = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT)
@click.argument("input", nargs=-1)
@click.option("-o", "--output", default=get_config("output"), hidden=(get_config("implementation")=="interpreter"), help="Name for output file.", show_default=True)
@click.option("-i", "--interactive", is_flag=True, hidden=(get_config("implementation")=="compiler"), help="Run in interative mode.")
@click.option("-d", "--debug", is_flag=True, help="Run in debug mode.")
@click.option("-f", "--force", is_flag=True, help="Force recompilation.")
@click.option("-x", "--clear", is_flag=True, help="Delete cached compiled files.")
def main(input: tuple, **flags):
    """Runs a compiled language with OPTIONS."""

    cfg: dict = get_config()

    cfg["input"] = list(input) # stored in config as a list
    cfg["output"] = flags.pop("output")
    cfg["flags"] = flags

    # check if the config has been modified (ignoring flags and input files)
    isModified = any(
        (cfg[category] != get_config(category))
        for category in cfg.keys() if not category in ("flags", "input")
    )

    set_config(cfg)
    

    print(f"magicc v{cfg["version"]} </> {cfg["language"]} {cfg["implementation"]}")


    if cfg["flags"]["clear"]:
        for filename in (
            "parser/AST.py", 
            "parser/eval.py",
            "parser/parsetable.py"
        ):
            if os.path.exists(filename):
                os.remove(filename) or print(f"Removed {filename}")
            else:
                print(f"{filename} not found")
        quit()


    if cfg["flags"]["force"] or isModified:
        processing.compile()


    from parser import evaluate


    for filename in input:
        with open(filename) as file:
            evaluate(file.read())

    if cfg["flags"]["interactive"]:
        for line in iter(lambda: get_input("</> "), "quit"):
            if line.strip():
                if cfg["flags"]["debug"]: start = time()
                evaluate(line)
                if cfg["flags"]["debug"]: print(f"Runtime: {time() - start}")    



# @cli.command
# @click.argument("tests", type=int, nargs=-1)
# def test(tests):
#     """Run specified built-in test cases; if none are specified, run all available. 
#     Recompiles before testing (except if locked)."""
    
#     if get_config("implementation") == "compiler":
#         return print("No test cases for compiled languages.")


#     processing.compile()

#     from tests import test

#     cfg = get_config()
#     cfg["tests"] = tests
#     set_config(cfg)
    
#     test(tests)



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        if get_config("flags", "debug"): raise e
        print(f"{type(e).__name__}: {e}")
