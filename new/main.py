from utils import *

import click
import os

from time import time



CONTEXT = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT)
@click.argument("input", nargs=-1)
@click.option("-o", "--output", default=CONFIG.output, hidden=(CONFIG.implementation=="interpreter"), help="Name for output file.", show_default=True)
@click.option("-i", "--interactive", is_flag=True, hidden=(CONFIG.implementation=="compiler"), help="Run in interative mode.")
@click.option("-d", "--debug", is_flag=True, help="Run in debug mode.")
@click.option("-f", "--force", is_flag=True, help="Force recompilation.")
@click.option("-x", "--reset", is_flag=True, help="Delete cached compiled files.")
def main(input: tuple, **flags):
    """Runs a compiled language with OPTIONS."""

    CONFIG.input = list(input) # stored in config as a list
    CONFIG.output = flags.pop("output")
    CONFIG.flags = flags


    print(f"magicc v{CONFIG.version} </> {CONFIG.language} {CONFIG.implementation}")


    if CONFIG.flags.reset:
        for filename in CONFIG.ignore.generated:
            filename = f"{CONFIG.paths.generated}/{filename}"
            if os.path.exists(filename):
                os.remove(filename) or print(f"Removed {filename}")
            else:
                print(f"{filename} not found")
        quit()


    if CONFIG.flags.force or CONFIG.isModified:
        
        import compiler

        with open(os.path.join(CONFIG.paths.language, "syntax.txt")) as file:
            compiler.evaluate(file.read())


    import parser

    for filename in input:
        with open(filename) as file:
            parser.evaluate(file.read())

    if CONFIG.flags.interactive:
        for line in iter(lambda: get_input("</> "), "quit"):
            if line.strip():
                if CONFIG.flags.debug: start = time()
                parser.evaluate(line)
                if CONFIG.flags.debug: print(f"Runtime: {time() - start}")    



if __name__ == "__main__":
    debug = CONFIG.flags.debug
    try:
        main()
    except Exception as e:
        if debug: raise e
        print(f"{type(e).__name__}: {e}")
    finally:
        CONFIG.save()
