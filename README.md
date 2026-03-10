# magicc: a general interpreter/compiler compiler

*magicc* is a system for simplified programming language development. As such, there are two primary ways to use it, and therefore two parallel guides. Those only interested in using the languages created by magicc can safely stop reading after the section titled [Basic Usage](#basic-usage). Those interested in using magicc for language development and prototyping should continue to the [Advanced Usage](#advanced-usage) section.


## Table of Contents


- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Advanced Usage](#advanced-usage)
- [Contributing](#contributing)
- [License](#license)


## Installation


### Requirements

magicc was developed using Python 3.12. Support for earlier versions is not guaranteed.

magicc uses [Nuitka](https://nuitka.net/user-documentation/) for compilation. It is strongly recommended to use a Python virtual environment for managing dependencies, which are provided in `.requirements`.

```bash
$ python3 -m venv example
$ source example/bin/activate
$ pip install -r .requirements
```

Nuitka requires `patchelf`.
```
$ sudo apt install patchelf
```

### Setup

In order to compile magicc projects, you will have to make the `magicc` file executable.

```
$ chmod +x magicc
```


## Basic Usage


For the sake of example, we will take the included language `banter` as an object case.

There are two ways to use a language with magicc: compile it or run it directly.

For the latter option, simply run `python3 main.py [<language folder>] <args>`. Valid <args> are:

- -i : interactive
- -t : run tests (only supported with certain built-in languages)
- -c : recompile syntax/semantics
- any input program for the specified language

This will generate `AST.py` and `eval.py` files. If `-c` is provided, the program builds the language from the specification files in the language folder; languages are saved after generation, so you can omit the folder and the `-c` flag on subsequent runs to use an already-generated language.

To compile a language using `magicc`, provide the language folder (which must contain at least a `syntax.txt` file) as the first argument, and the name of the output executable as the second argument.

```
$ ./magicc languages/banter banter
```

This will generate a binary file `banter`, which can be run as a normal executable. Only `-i` and `-t` are supported for languages compiled in this way; `-c` can only be used when running the language 'ad-hoc', e.g.

```
$ ./banter -i
```
or
```
$ ./banter ../examples/factoral.banter
```
or
```
$ python3 main.py languages/banter -c -i
```

If no `semantics.py` file is included in the language folder, evaluation defaults to returning the string literal.


## Advanced Usage


### Introduction

To develop languages with magicc, it is recommended to peruse the `AST_generator.py` and output `eval.py`/`AST.py` files. Generally speaking, a language requires only two files: a `syntax.txt` and a `semantics.py`. The latter is not necessary if no evaluation is wanted.

magicc provides a few modules which handle basic datatypes (lists, strings, numbers). Everything else must be user-defined. To include a dependency, use `#require <dependency>` in the syntax file.

### BNF Syntax

By default, all rules are space-agnostic; to exclude spaces altogether, include a ! at the beginning of the rule name, e.g. `<!INT> ::= <INT> <DIGIT> | <DIGIT>`. This is the only deviation from standard BNF syntax permitted, although certain things (the alternation symbol |, for example) can be temporarily overridden.

### Adding Semantics

Semantic rules are simply Python functions which match the proper syntax. By default, if no semantics are provided for a rule, the behavior is to evaluate and return the first element. This eliminates many unnecessary duplicate rules, since only more complex semantics require explicit functions.

Semantic rule names are of the form `p_<rulename>`. If a production rule has multiple alternatives, a specific alternative can be matched with a `_<#>` at the end, where the number corresponds to the index (from 0) of the alternative. Any remaining alternatives will use either the general `p_<rulename>` or the built-in default.

e.g.

The following semantic functions evaluate the rule `<!INT> ::= <INT> <DIGIT> | <DIGIT>`.

```py
def p_int_0(expr): # matches the 0th alternative of the <!INT> production rule
    return int(f"{expr(0)}{expr(1)}")

def p_int(expr): # matches all other cases
    return int(expr(0))
```

The `eval.py` file combines provided semantics into a single evaluation function. This can be used to either interpret or compile parsed syntax.

### Evaluation

As the evaluation traverses the AST, child nodes are converted into lazy functions constructed from the semantic rules associated with each production provided by the `semantics.py` files. Each semantic function receives an `expr`, which is simply a wrapper containing a dispatch dictionary of the semantic rules. So the example `<!INT>` rule (0th alternative), evaluated with `p_int_0`, accesses `expr(0)` and `expr(1)`, respectively corresponding to `<INT>` and `<DIGIT>` in the rule. For a better understanding, see the `EVAL` section of a generated `AST.py` file.


## Contributing


If you have ideas for interesting features, find or fix a bug, or notice a typo, please feel free to contribute via a pull request.


## License

magicc is licensed under a [GNU General Public License](https://github.com/Antonio-Iijima/CFG-Parser/blob/main/LICENSE).
