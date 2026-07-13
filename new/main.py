from utils import *

import cloup
import os



CONTEXT = dict(help_option_names=['-h', '--help'])


@cloup.command(context_settings=CONTEXT)
@cloup.argument("input", nargs=-1)
@cloup.option("-o", "--output", default=CONFIG.output, hidden=(CONFIG.implementation=="interpreter"), help="Name for output file.", show_default=True)
@cloup.option("-i", "--interactive", is_flag=True, hidden=(CONFIG.implementation=="compiler"), help="Run in interative mode.")
@cloup.option("-d", "--debug", is_flag=True, help="Run in debug mode.")
@cloup.option("-f", "--force", is_flag=True, help="Force recompilation.")
@cloup.option("-x", "--reset", is_flag=True, help="Delete cached compiled files.")
def main(input: tuple, **flags):
    """Runs a compiled language with OPTIONS."""

    CONFIG.input = list(input)
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
                
                try:
                    result = parser.evaluate(line)
                    if result is not None: print(result)

                except Exception as e:
                    if CONFIG.flags.debug: raise e
                    else: print(f"{type(e).__name__}: {e}")



if __name__ == "__main__":
    try:
        main()
    finally:
        CONFIG.save()
