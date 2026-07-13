### Program Flow
---

- compile.py
  - metacircular compilation
  - standard compilation

- main.py
  - file interpretation
```
python3 main.py ../examples/interpreter.lsp
Call                    File
compiler.compile()      main.py

```



### Files
---


```
> src/
    > parser/
        | __init__.py
        | parserdata.py
        | evaluation.py
        > backup/
            | { old copies of everything in parser/ }
    ...
```


### Structure
---

- \_\_init__.py
  - parse function
- parsetable.py
  - TERMINALS
  - RULES
  - TABLE


### Necessary Functions
---




- parse(input: str) -> AST
  - LALR parse based on data in `parser/parserdata`
    - requires: `TERMINALS`, 
  - Integrated lexer
- evaluate(string: str) -> any
  - wrapper for `parse`
  - converts AST to `Expr` and calls `parser/evaluation`'s evaluation function
    - require `_evaluate`, `Parser`?
  


`parse` needs:
- PROGRAM
- Token
- Error messages
- Rule
- RULES
- TABLE
- TERMINALS