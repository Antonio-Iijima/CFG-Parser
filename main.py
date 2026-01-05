from parser_generator import generate

from os.path import abspath, exists
from os import listdir, remove
from sys import argv



if __name__ == "__main__":

    if '-x' in argv:
        exists("parser.py") and remove("parser.py")
        exists("eval.py") and remove("eval.py")
        quit()

    iFlag = "-i" in argv 
    iFlag and argv.remove("-i")

    dFlag = "-d" in argv 
    dFlag and argv.remove("-d")
    
    vFlag = "-v" in argv 
    vFlag and argv.remove("-v")


    if len(argv) > 1:
        path = abspath(argv[0])
        language = abspath(argv[1])
        for file in (s for s in listdir(language) if not s.startswith("__")):
            path = f"{language}/{file}"
            match file:
                case "semantics.py":
                    SEMANTICS = path
                case "syntax.txt":
                    with open(path) as text: 
                        SYNTAX = [line for line in text.readlines() if not line.startswith("--")]
                case _:
                    print(f"Unrecognized file: {path}")
    else:
        print("Language folder not found.")
        quit()


    print()
    generate(
        syntax=SYNTAX,
        semantics=SEMANTICS,
        debug=dFlag
    )
    print()


    if iFlag:

        from parser import parse, validate
        from eval import evaluate

        for line in iter(lambda: input("> "), "quit"):
            if vFlag: print(validate(line))
            print(evaluate(parse(line)))
