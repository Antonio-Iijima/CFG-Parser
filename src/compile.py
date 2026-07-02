from utils import get_config, set_config
from main import CONTEXT

import processing

import PyInstaller.__main__
import click
import os



@click.command(context_settings=CONTEXT)
@click.argument("path", type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option("-i", "--interpreter", "implementation", flag_value="interpreter", help="Compile an interpreter.", default=True)
@click.option("-c", "--compiler", "implementation", flag_value="compiler", help="Compile a compiler.")
@click.option("-o", "--onefile", "onefile", is_flag=True, help="Generate single file executable.")
def main(path: str, implementation: bool, onefile: bool):
    """Compiles a language system from the files provided in PATH."""

    cfg = get_config()

    path = path.split("/")

    cfg["paths"]["language"] = "/".join(path[-2:])
    cfg["language"] = path[-1]
    cfg["implementation"] = implementation

    set_config(cfg)

    processing.compile()

    if onefile:

        PyInstaller.__main__.run([
            "main.py",
            "--onefile",
            f"--name={cfg["language"]}",
            "--add-data", "config.json:."
        ])

        os.system("rm -r build && rm ./*.spec")



if __name__ == "__main__":
    main()
