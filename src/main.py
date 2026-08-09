from utils import *

import cloup
import os



CONTEXT = dict(help_option_names=['-h', '--help'])



@cloup.command(context_settings=CONTEXT)
@cloup.argument("input", nargs=-1)
@cloup.option("-o", "--output", default=CONFIG.output, hidden=(CONFIG.implementation=="interpreter"), help="Name for output file.", show_default=True)
@cloup.option("-i", "--interactive", is_flag=True, hidden=(CONFIG.implementation=="compiler"), help="Run in interative mode.")
@cloup.option("-d", "--debug", is_flag=True, help="Run in debug mode.")
@cloup.option("-v", "--verbose", is_flag=True, help="Allow warning/miscellaneous messages.")
@cloup.option("-t", "--time", is_flag=True, help="Print runtime after each parse.")
@cloup.option("-f", "--force", is_flag=True, help="Force recompilation.")
@cloup.option("-x", "--reset", is_flag=True, help="Delete cached compiled files.")
def main(input: tuple, **flags):
    """Runs a compiled language with OPTIONS."""

    print(CONFIG.info)


    CONFIG.output = flags.pop("output")
    CONFIG.flags.update(flags)


    if CONFIG.flags.reset:
        path = os.path.join(CONFIG.paths.root, "parser")
        for filename in os.listdir(path):
            file = os.path.join(path, filename)
            if os.path.isfile(file):
                if filename.startswith("__"): continue
                os.remove(file) or print(f"Removed parser/{filename}")
        quit()


    if CONFIG.flags.force or CONFIG.isModified:
        
        import compiler

        with open(os.path.join(CONFIG.paths.language, "syntax.txt")) as file:
            compiler.evaluate(file.read())


    import parser


    def eval_print(text: str) -> None:
        try:
            result = parser.evaluate(text)
            if result is not None: print(result)
        except Exception as e:
            if CONFIG.flags.debug: raise e
            else: print(f"{type(e).__name__}: {e}")


    warnings = {}
    for filename in input:
        try:
            with open(filename) as file:
                eval_print(file.read())
        except FileNotFoundError as e:
            note = e.strerror.lower()
            if not note in warnings: warnings[note] = []
            warnings[note].append(e.filename)
    print_warnings("file not found", warnings)


    if CONFIG.flags.interactive:
        for input in iter(lambda: get_input("</> "), "quit"):
            if (input is not None) and input.strip():
                eval_print(input)



if __name__ == "__main__":
    try:
        main()
    finally:
        CONFIG.save()
