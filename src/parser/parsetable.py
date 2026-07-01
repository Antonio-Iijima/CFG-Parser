from parser.AST import *


        
RULES = (
    ProductionData( # <START> ::= <PROGRAM>
            START, 'MAIN', 0, [PROGRAM]),
    ProductionData( # <PROGRAM> ::= <BOOLEXPR>
            PROGRAM, 'MAIN', 0, [BOOLEXPR]),
    ProductionData( # <PROGRAM> ::= <BOOLEXPR> \n+ <PROGRAM>
            PROGRAM, 'MAIN', 1, [BOOLEXPR, r'\n+', PROGRAM]),
    ProductionData( # <BOOLEXPR> ::= \( <LIST> , <EXPR> \)
            BOOLEXPR, 'MAIN', 0, [r'\(', LIST, r',', EXPR, r'\)']),
    ProductionData( # <LIST> ::= \[ \]
            LIST, 'MAIN', 0, [r'\[', r'\]']),
    ProductionData( # <LIST> ::= \[ <ATOMS> \]
            LIST, 'MAIN', 1, [r'\[', ATOMS, r'\]']),
    ProductionData( # <ATOMS> ::= <ATOM>
            ATOMS, 'MAIN', 0, [ATOM]),
    ProductionData( # <ATOMS> ::= <ATOM> , <ATOMS>
            ATOMS, 'MAIN', 1, [ATOM, r',', ATOMS]),
    ProductionData( # <ATOM> ::= <VAR>
            ATOM, 'MAIN', 0, [VAR]),
    ProductionData( # <EXPR> ::= <AND> \| <EXPR>
            EXPR, 'MAIN', 0, [AND, r'\|', EXPR]),
    ProductionData( # <EXPR> ::= <AND>
            EXPR, 'MAIN', 1, [AND]),
    ProductionData( # <AND> ::= <NOT> & <AND>
            AND, 'MAIN', 0, [NOT, r'&', AND]),
    ProductionData( # <AND> ::= <NOT>
            AND, 'MAIN', 1, [NOT]),
    ProductionData( # <NOT> ::= <VAR>
            NOT, 'MAIN', 2, [VAR]),
    ProductionData( # <NOT> ::= ~ <NOT>
            NOT, 'MAIN', 0, [r'~', NOT]),
    ProductionData( # <NOT> ::= <LITERAL>
            NOT, 'MAIN', 1, [LITERAL]),
    ProductionData( # <LITERAL> ::= t
            LITERAL, 'MAIN', 0, [r't']),
    ProductionData( # <LITERAL> ::= f
            LITERAL, 'MAIN', 1, [r'f']),
    ProductionData( # <VAR> ::= [a-eg-su-z]
            VAR, 'MAIN', 0, [r'[a-eg-su-z]'])
)



TABLE = { 
    0 : {
        PROGRAM : [('G', 1)],
        BOOLEXPR : [('G', 2)],
        r'\(' : [('S', 5)]
    },
    1 : {
        EOI : [('A', True)]
    },
    2 : {
        EOI : [('R', 1)],
        r'\n+' : [('S', 3)]
    },
    3 : {
        PROGRAM : [('G', 4)],
        BOOLEXPR : [('G', 2)],
        r'\(' : [('S', 5)]
    },
    4 : {
        EOI : [('R', 2)]
    },
    5 : {
        LIST : [('G', 6)],
        r'\[' : [('S', 23)]
    },
    6 : {
        r',' : [('S', 7)]
    },
    7 : {
        EXPR : [('G', 8)],
        AND : [('G', 10)],
        NOT : [('G', 13)],
        LITERAL : [('G', 16)],
        r'f' : [('S', 17)],
        r't' : [('S', 18)],
        r'~' : [('S', 19)],
        VAR : [('G', 21)],
        r'[a-eg-su-z]' : [('S', 22)]
    },
    8 : {
        r'\)' : [('S', 9)]
    },
    9 : {
        r'\n+' : [('R', 3)],
        EOI : [('R', 3)]
    },
    10 : {
        r'\)' : [('R', 10)],
        r'\|' : [('S', 11)]
    },
    11 : {
        EXPR : [('G', 12)],
        AND : [('G', 10)],
        NOT : [('G', 13)],
        LITERAL : [('G', 16)],
        r'f' : [('S', 17)],
        r't' : [('S', 18)],
        r'~' : [('S', 19)],
        VAR : [('G', 21)],
        r'[a-eg-su-z]' : [('S', 22)]
    },
    12 : {
        r'\)' : [('R', 9)]
    },
    13 : {
        r'\)' : [('R', 12)],
        r'\|' : [('R', 12)],
        r'&' : [('S', 14)]
    },
    14 : {
        AND : [('G', 15)],
        NOT : [('G', 13)],
        LITERAL : [('G', 16)],
        r'f' : [('S', 17)],
        r't' : [('S', 18)],
        r'~' : [('S', 19)],
        VAR : [('G', 21)],
        r'[a-eg-su-z]' : [('S', 22)]
    },
    15 : {
        r'\)' : [('R', 11)],
        r'\|' : [('R', 11)]
    },
    16 : {
        r'\)' : [('R', 15)],
        r'&' : [('R', 15)],
        r'\|' : [('R', 15)]
    },
    17 : {
        r'\)' : [('R', 17)],
        r'&' : [('R', 17)],
        r'\|' : [('R', 17)]
    },
    18 : {
        r'\)' : [('R', 16)],
        r'&' : [('R', 16)],
        r'\|' : [('R', 16)]
    },
    19 : {
        NOT : [('G', 20)],
        LITERAL : [('G', 16)],
        r'f' : [('S', 17)],
        r't' : [('S', 18)],
        r'~' : [('S', 19)],
        VAR : [('G', 21)],
        r'[a-eg-su-z]' : [('S', 22)]
    },
    20 : {
        r'\)' : [('R', 14)],
        r'&' : [('R', 14)],
        r'\|' : [('R', 14)]
    },
    21 : {
        r'\)' : [('R', 13)],
        r'&' : [('R', 13)],
        r'\|' : [('R', 13)]
    },
    22 : {
        r'\)' : [('R', 18)],
        r',' : [('R', 18)],
        r'\]' : [('R', 18)],
        r'&' : [('R', 18)],
        r'\|' : [('R', 18)]
    },
    23 : {
        r'\]' : [('S', 24)],
        ATOMS : [('G', 25)],
        ATOM : [('G', 27)],
        VAR : [('G', 30)],
        r'[a-eg-su-z]' : [('S', 22)]
    },
    24 : {
        r',' : [('R', 4)]
    },
    25 : {
        r'\]' : [('S', 26)]
    },
    26 : {
        r',' : [('R', 5)]
    },
    27 : {
        r'\]' : [('R', 6)],
        r',' : [('S', 28)]
    },
    28 : {
        ATOMS : [('G', 29)],
        ATOM : [('G', 27)],
        VAR : [('G', 30)],
        r'[a-eg-su-z]' : [('S', 22)]
    },
    29 : {
        r'\]' : [('R', 7)]
    },
    30 : {
        r'\]' : [('R', 8)],
        r',' : [('R', 8)]
    }
}